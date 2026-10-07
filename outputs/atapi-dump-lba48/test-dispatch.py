"""Execute the exact candidate selector bytes across address/capability boundaries."""
import hashlib
import json
import random
import struct
import sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
data=(k/'artifacts/atapi-candidate0105.sys').read_bytes();p=pefile.PE(data=data)
base=0x100000;adapter=0x200000;srb=0x202000;stack=0x210000;done=0x220000
u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,0x20000);u.mem_write(base,p.get_memory_mapped_image())
u.mem_map(adapter,0x30000)
endpoints={base+0x258c:'extended',base+0x27fe:'legacy',done:'rejected'}
hit=[];writes=[]
def code(uc,address,size,unused):
    if address in endpoints:hit.append(endpoints[address]);uc.emu_stop()
u.hook_add(UC_HOOK_CODE,code)
u.hook_add(UC_HOOK_MEM_WRITE,lambda uc,access,address,size,value,unused:writes.append((address,size,value)))
rng=random.Random(105);cases=[]
for lba in [0,1,0xffffffe,0xfffffff,0x10000000,0x1147dc70,0xffffff00,0xffffffff]:
    for count in [0,1,8,128,256,257]:
        for flag in [False,True]:
            for target in [0,1,3,4]:cases.append((lba,count*512,flag,target,0x39,0x2a))
for i in range(4096):
    cases.append((rng.randrange(1<<32),rng.choice([511,512,513,4096,32768,131072,131073]),
                  bool(rng.randrange(2)),rng.randrange(5),rng.choice([0,0x39,0xc5]),rng.choice([0x2a,0x28])))
counts={n:0 for n in endpoints.values()}
for lba,size,capable,target,command,opcode in cases:
    hit.clear();writes.clear();u.mem_write(adapter,b'\0'*0x1000);u.mem_write(srb,b'\0'*64)
    u.mem_write(adapter+target*4+0xb0,struct.pack('<I',0x400000 if capable else 0))
    u.mem_write(adapter+target*0x3c+0x910,bytes([command]))
    u.mem_write(srb+6,bytes([target]));u.mem_write(srb+0x30,bytes([opcode]))
    u.mem_write(srb+0x10,struct.pack('<I',size));u.mem_write(srb+0x32,struct.pack('>I',lba))
    u.mem_write(stack,struct.pack('<3I',done,adapter,srb))
    for reg in [UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX]:u.reg_write(reg,0xa5a5a5a5)
    for reg in [UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI]:u.reg_write(reg,0x12345678)
    u.reg_write(UC_X86_REG_ESP,stack);u.reg_write(UC_X86_REG_EFLAGS,2)
    valid=opcode==0x2a and target<4 and 0<size<=131072 and size%512==0 and lba+size//512-1<=0xffffffff
    expected=('extended' if command==0x39 else 'rejected') if valid and capable else 'legacy' if valid and lba+size//512-1<=0xfffffff else 'rejected'
    u.emu_start(base+0x15800,0,count=100)
    assert hit==[expected],(lba,size,capable,target,command,opcode,hit,expected)
    assert not writes
    assert all(u.reg_read(reg)==0x12345678 for reg in [UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI])
    assert u.reg_read(UC_X86_REG_ESP)==stack+(12 if expected=='rejected' else 0)
    if expected=='rejected':assert u.reg_read(UC_X86_REG_EAX)==6
    else:assert bytes(u.mem_read(stack,12))==struct.pack('<3I',done,adapter,srb)
    counts[expected]+=1
r=dict(passed=True,executed_cases=len(cases),routes=counts,zero_memory_writes=True,callee_saved_preserved=True,
    exact_candidate_sha256=hashlib.sha256(data).hexdigest(),test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    limits='Host instruction execution validates selector/ABI/guards only; no ATA device, guest driver load, dump persistence or recovery qualification.')
(k/'host-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
