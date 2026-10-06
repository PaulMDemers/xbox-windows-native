"""Isolated x86 replay of owned NT5 checksum arithmetic; not a guest boot."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EAX
kernel=(k.parent/'native-windows-physical-f/package/F/winnt/system32/ntoskrnl.exe').read_bytes()
assert hashlib.sha256(kernel).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
p=pefile.PE(data=kernel);base=p.OPTIONAL_HEADER.ImageBase;image=p.get_memory_mapped_image()
original=(k.parent/'video-direct-map/artifacts/xboxvnt5.sys').read_bytes();mapped=(k/'003/mapped-238.bin').read_bytes()
assert mapped[:len(original)]==original and mapped[len(original)]==0x97
def replay(tail):
    u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x200000);u.mem_write(base,image)
    start=0x1000000;stack=0x2000000;sentinel=0x3000000
    u.mem_map(start,0x20000);u.mem_write(start,original+bytes([tail])+mapped[len(original)+1:])
    u.mem_map(stack,0x10000);u.mem_map(sentinel,4096);sp=stack+0x8000
    u.mem_write(sp,struct.pack('<III',sentinel,start,len(original)));u.reg_write(UC_X86_REG_ESP,sp)
    def hook(uc,at,size,unused):
        if at==base+0x5a986:
            # Stub only header lookup; checksum instructions run unmodified.
            esp=uc.reg_read(UC_X86_REG_ESP);ret,arg=struct.unpack('<II',uc.mem_read(esp,8))
            assert bytes(uc.mem_read(arg,2))==b'MZ'
            header=arg+struct.unpack('<I',uc.mem_read(arg+60,4))[0]
            assert bytes(uc.mem_read(header,4))==b'PE\0\0'
            uc.reg_write(UC_X86_REG_EAX,header);uc.reg_write(UC_X86_REG_ESP,esp+8);uc.reg_write(UC_X86_REG_EIP,ret)
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start(base+0xf58be,sentinel,count=1000000)
    assert u.reg_read(UC_X86_REG_EIP)==sentinel
    return u.reg_read(UC_X86_REG_EAX)
observed=replay(0x97);zeroed=replay(0);assert observed==0 and zeroed==1
mp=pefile.PE(data=original)
r=dict(scope=__doc__,kernel_sha256=hashlib.sha256(kernel).hexdigest(),file_sha256=hashlib.sha256(original).hexdigest(),
       file_bytes=len(original),exact_file_match_in_guest_mapping=True,stored_checksum=hex(mp.OPTIONAL_HEADER.CheckSum),
       independently_computed_checksum=hex(mp.generate_checksum()),observed_eof_byte=0x97,
       original_tail_return=observed,zero_tail_return=zeroed,passed=True,
       limits='Host Unicorn replay with RtlImageNtHeader stubbed; only one byte beyond EOF changed in replay memory. No live guest edits. Third captured mapping in trace003 is not the miniport; last-image-entry labels are hints across concurrent calls.')
(k/'checksum-replay.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
