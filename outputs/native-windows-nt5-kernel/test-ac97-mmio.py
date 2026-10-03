"""Execute the experimental ACI resource and register boundaries, not sound emulation."""
import pathlib,sys,struct,json,hashlib
out=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(out.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
code=(out/'test-boundary.py').read_text();ns={};exec(code[code.index('def symbols(p):'):code.index('sym=symbols(h)')],{'struct':struct},ns)
file=out/'artifacts/ac97xnt5.sys';pe=pefile.PE(str(file));sym=ns['symbols'](pe);base=pe.OPTIONAL_HEADER.ImageBase
STACK=0x800000;OBJ=STACK+0x1000;RESOURCE=OBJ+0x100;VTABLE=RESOURCE+0x100;DESC=VTABLE+0x100;STOP=0xa00000;MMIO=0xb00000
class Machine:
 def __init__(self,counts=None,length=0x1000,descriptor=True):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);self.hooks={STOP:self.stop};self.calls=[];self.counts=counts or {1:0,2:1,3:1,4:0};self.descriptor=descriptor;self.stopped=False
  for addr,size in [(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),(STACK,0x10000),(STOP,0x1000),(MMIO,0x1000)]:self.u.mem_map(addr,size)
  self.u.mem_write(base,pe.get_memory_mapped_image());self.put(OBJ+32,MMIO+0x100);self.put(RESOURCE,VTABLE);self.put(VTABLE+16,STOP+16);self.put(VTABLE+20,STOP+32);self.put(DESC+4,0xfec00000);self.put(DESC+12,length)
  self.hooks[STOP+16]=self.count;self.hooks[STOP+32]=self.find
  for i,imp in enumerate(imp for lib in pe.DIRECTORY_ENTRY_IMPORT for imp in lib.imports):
   address=STOP+0x100+i*16;self.put(imp.address,address);name=imp.name.decode();self.hooks[address]=lambda n=name:self.imported(n)
  self.u.hook_add(UC_HOOK_CODE,lambda u,a,size,ctx:self.hooks[a]() if a in self.hooks else None)
 def get(self,p):return struct.unpack('<I',self.u.mem_read(p,4))[0]
 def put(self,p,v):self.u.mem_write(p,struct.pack('<I',v&0xffffffff))
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(self,n,value=0):
  sp=self.u.reg_read(UC_X86_REG_ESP);self.u.reg_write(UC_X86_REG_EAX,value);self.u.reg_write(UC_X86_REG_EIP,self.get(sp));self.u.reg_write(UC_X86_REG_ESP,sp+4+4*n)
 def stop(self):self.stopped=True;self.u.emu_stop()
 def count(self):obj,kind=self.args(2);assert obj==RESOURCE;self.ret(2,self.counts[kind])
 def find(self):obj,kind,index=self.args(3);assert (obj,kind,index)==(RESOURCE,3,0);self.ret(3,DESC if self.descriptor else 0)
 def imported(self,name):
  if name=='MmMapIoSpace':self.calls.append((name,*self.args(4)));self.ret(4,0);return
  assert name.startswith(('READ_REGISTER_','WRITE_REGISTER_')),name
  width={'UCHAR':1,'USHORT':2,'ULONG':4}[name.split('_')[-1]]
  args=self.args(1 if name.startswith('READ') else 2);self.calls.append((name,*args));assert MMIO<=args[0] and args[0]+width<=MMIO+0x180
  if name.startswith('READ'):self.ret(1,int.from_bytes(self.u.mem_read(args[0],width),'little'))
  else:self.u.mem_write(args[0],(args[1]&((1<<(8*width))-1)).to_bytes(width,'little'));self.ret(2)
 def run(self,name,args,stdcall=True):
  self.stopped=False;sp=STACK+0xf000
  for i,value in enumerate([STOP,*args]):self.put(sp+4*i,value)
  self.u.reg_write(UC_X86_REG_ESP,sp);self.u.emu_start(sym[name],0,count=50000);assert self.stopped
  assert self.u.reg_read(UC_X86_REG_ESP)==sp+4+(4*len(args) if stdcall else 0)
  return self.u.reg_read(UC_X86_REG_EAX)
results=[]
for bits,suffix in [(8,'h'),(16,'t'),(32,'m')]:
 m=Machine();width=bits//8;offset={8:0x1b,16:0x16,32:0x10}[bits];value=0x89abcdef&((1<<bits)-1)
 name=next(n for n in sym if 'WriteBMControlRegisterEm'+suffix+'@12' in n);m.run(name,(OBJ,offset,value))
 name=next(n for n in sym if 'ReadBMControlRegister'+str(bits)+'Em@8' in n);assert m.run(name,(OBJ,offset))==value
 assert len(m.calls)==2 and m.calls[0][1]==MMIO+0x100+offset
results.append('8/16/32-bit bus-master accesses use MMIO at the ACI +0x100 aperture and preserve the stdcall ABI')
validate='__Z17ValidateResourcesP13IResourceList'
assert Machine().run(validate,(RESOURCE,),False)==0
for kwargs in [{'counts':{1:2,2:1,3:1,4:0}},{'counts':{1:0,2:0,3:1,4:0}},{'counts':{1:0,2:1,3:2,4:0}},{'counts':{1:0,2:1,3:1,4:1}},{'length':0x17f},{'descriptor':False}]:
 assert Machine(**kwargs).run(validate,(RESOURCE,),False)==0xc0000182
results.append('Rejects PC I/O-port resources, absent IRQs, extra memory/DMA resources, absent descriptors and undersized MMIO')
name=next(n for n in sym if 'CAC97AdapterCommon4InitE' in n)
for kwargs in [{'length':0x17f},{'descriptor':False},{}]:
 m=Machine(**kwargs);status=m.run(name,(OBJ,RESOURCE,0x1234));assert status==(0xc000009a if not kwargs else 0xc0000182)
 if not kwargs:assert m.calls==[('MmMapIoSpace',0xfec00000,0,0x180,0)]
 else:assert not m.calls
results.append('Mapping failures propagate without touching unmapped registers; maps only 0x180 uncached bytes')
name=next(n for n in sym if 'CAC97AdapterCommon18WriteCodecRegister' in n)
for register in [23,24,27,28]:
 m=Machine();assert m.run(name,(OBJ,register,0x1234,0xffff))==0xc00000bb;assert not m.calls
results.append('Absent surround/LFE codec registers return not-supported without an MMIO write')
report={'scope':__doc__,'driver_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'tests':[{'test':s,'passed':True} for s in results]}
(out/'ac97-mmio-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(len(results),'ACI boundary groups passed')
