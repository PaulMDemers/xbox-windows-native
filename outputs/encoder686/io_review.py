"""Execute the actual nxdk COFF port-read functions with simulated port values.
This validates instruction widths, preservation and bounded return, not physical timer rate.
"""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('C:/xwn686/build001')
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_INSN
from unicorn.x86_const import UC_X86_INS_IN,UC_X86_INS_OUT,UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
out=K/'io-review001.json';assert not out.exists()
b=(P/'io.obj').read_bytes(); sha=lambda v:hashlib.sha256(v).hexdigest()
r={'passed':False,'object_sha256':sha(b),'source_sha256':sha((P/'io.c').read_bytes()),
   'scope':'actual nxdk 32-bit COFF functions under Unicorn; simulated IN values', 'cases':[]}
try:
    machine,nsec,_,symptr,nsyms,optsz,_=struct.unpack_from('<HHLLLHH',b)
    assert machine==0x14c and optsz==0
    strings=b[symptr+18*nsyms:]
    sections=[]
    for i in range(nsec):
        h=struct.unpack_from('<8sLLLLLLHHL',b,20+40*i)
        sections.append({'size':h[3],'raw':h[4],'reloc_count':h[7]})
    symbols={};i=0
    while i<nsyms:
        name,value,section,typ,storage,aux=struct.unpack_from('<8sLhHBB',b,symptr+18*i)
        if name[:4]==b'\0'*4:
            off=struct.unpack('<L',name[4:])[0];name=strings[off:].split(b'\0')[0]
        else:name=name.split(b'\0')[0]
        if section>0:symbols[name.decode()]=(section,value)
        i+=aux+1
    for name,port,width,mask in [('_raw_pm',0x8008,4,0xffffffff),('_raw_smbus_status',0xc000,2,0xffff)]:
        section,offset=symbols[name];s=sections[section-1];assert s['reloc_count']==0
        code=b[s['raw']:s['raw']+s['size']]
        for value in [0,1,0x00ffffff,0x01000000,0x12345678,0x80000000,0xffffffff]:
            u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0x100000,0x10000);u.mem_map(0x200000,0x10000)
            u.mem_write(0x100000,code);u.reg_write(UC_X86_REG_ESP,0x208000)
            u.mem_write(0x208000,struct.pack('<LL',0x10ff00,0))
            reads=[];writes=[]
            def pin(uc,p,w,_):reads.append([p,w]);return value & mask
            def pout(uc,p,w,v,_):writes.append([p,w,v])
            u.hook_add(UC_HOOK_INSN,pin,None,1,0,UC_X86_INS_IN)
            u.hook_add(UC_HOOK_INSN,pout,None,1,0,UC_X86_INS_OUT)
            u.emu_start(0x100000+offset,0x10ff00,count=100)
            assert u.reg_read(UC_X86_REG_EIP)==0x10ff00
            actual=u.reg_read(UC_X86_REG_EAX)&mask
            assert reads==[[port,width]] and not writes and actual==value&mask
            r['cases'].append({'symbol':name,'input':value,'result':actual,'reads':reads,'writes':writes})
    r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS actual nxdk IN32/IN16: 14 cases, no OUT instructions executed')
