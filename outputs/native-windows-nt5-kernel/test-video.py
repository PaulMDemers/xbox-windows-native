"""Execute the miniport binary with modeled video-port calls and NV2A registers."""
import pathlib,sys,json,hashlib,struct
out=pathlib.Path(__file__).resolve().parent;root=out.parents[1];sys.path.insert(0,str(root/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
code=(out/'test-boundary.py').read_text();ns={};exec(code[code.index('def symbols(p):'):code.index('sym=symbols(h)')],{'struct':struct},ns)
path=out/'artifacts/xboxvnt5.sys';pe=pefile.PE(str(path));sym=ns['symbols'](pe);base=pe.OPTIONAL_HEADER.ImageBase
vp=pefile.PE(str(out/'installed-files/WINNT/system32/drivers/videoprt.sys'));exports={s.name.decode() for s in vp.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
assert all(i.name.decode() in exports for lib in pe.DIRECTORY_ENTRY_IMPORT for i in lib.imports)
STACK=0x800000;EXT=STACK+0x1000;REQ=STACK+0x2000;STATUS=REQ+64;INPUT=REQ+128;OUTPUT=REQ+256;MMIO=0x10000000;STOP=0xa00000;TRAMP=STOP+0x100
results=[]
class Machine:
 def __init__(self,offset=0x3c00000,width=640,pitch=2560,format=3,map_status=0):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);u=self.u;self.hooks={STOP:self.stop};self.calls=[];self.freed=[];self.stopped=False;self.map_status=map_status
  for addr,size in [(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),(STACK,0x10000),(STOP,0x1000),(MMIO,0x700000)]:u.mem_map(addr,size)
  u.mem_write(base,pe.get_memory_mapped_image());self.put(MMIO+0x680838,width-1);self.put(MMIO+0x680818,479);self.put(MMIO+0x600800,offset)
  self.crtc={0x13:(pitch//8)&255,0x19:((pitch//8)>>3)&0xe0,0x28:format}
  n=0
  for lib in pe.DIRECTORY_ENTRY_IMPORT:
   for imp in lib.imports:
    addr=TRAMP+n*16;n+=1;self.put(imp.address,addr);self.hooks[addr]=getattr(self,imp.name.decode())
  u.hook_add(UC_HOOK_CODE,lambda u,a,size,ctx:self.hooks[a]() if a in self.hooks else None)
  u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def get(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def stop(self):self.stopped=True;self.u.emu_stop()
 def write(self,u,access,address,size,value,ctx):
  if address==MMIO+0x6013d4:self.u.mem_write(MMIO+0x6013d5,bytes([self.crtc.get(value,0)]))
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(self,n,value=0):
  sp=self.u.reg_read(UC_X86_REG_ESP);ip=self.get(sp);self.u.reg_write(UC_X86_REG_EAX,value);self.u.reg_write(UC_X86_REG_ESP,sp+4+n*4);self.u.reg_write(UC_X86_REG_EIP,ip)
 def run(self,name,args=()):
  self.stopped=False;sp=STACK+0xf000
  for i,v in enumerate([STOP,*args]):self.put(sp+i*4,v)
  self.u.reg_write(UC_X86_REG_ESP,sp);self.u.emu_start(sym[name],0,count=50000)
  assert self.stopped and self.u.reg_read(UC_X86_REG_ESP)==sp+4+len(args)*4
  return self.u.reg_read(UC_X86_REG_EAX)
 def VideoPortZeroMemory(self):
  p,n=self.args(2);self.u.mem_write(p,bytes(n));self.ret(2)
 def VideoPortGetAccessRanges(self):
  ext,requested,requests,count,ptr,vendor,device,slot=self.args(8)
  assert ext==EXT and requested==0 and count==3
  assert bytes(self.u.mem_read(vendor,2))==b'\xde\x10' and bytes(self.u.mem_read(device,2))==b'\xa0\x02'
  self.u.mem_write(ptr,struct.pack('<QIBBBx',0xfd000000,0x1000000,0,1,0)+struct.pack('<QIBBBx',0xf0000000,0x8000000,0,1,0)+bytes(16));self.ret(8)
 def VideoPortGetDeviceBase(self):
  ext,lo,hi,length,io=self.args(5);assert (ext,lo,hi,length,io)==(EXT,0xfd000000,0,0x681000,0);self.ret(5,MMIO)
 def VideoPortFreeDeviceBase(self):self.freed.append(self.args(2));self.ret(2)
 def VideoPortInitialize(self):
  one,two,ptr,ctx=self.args(4);self.init=bytes(self.u.mem_read(ptr,80));assert self.get(ptr)==80 and self.get(ptr+24)==128;self.ret(4,0)
 def VideoPortMapMemory(self):
  ext,lo,hi,length,space,ptr=self.args(6);self.calls.append((lo,hi,self.get(length),self.get(space)))
  self.put(ptr,0x90000000);self.ret(6,self.map_status)
 def VideoPortUnmapMemory(self):self.calls.append(self.args(3));self.ret(3)
 def init_adapter(self):
  assert self.run('_Nt5VideoFindAdapter@20',(EXT,0,0,OUTPUT,OUTPUT+128))==0
  assert self.u.mem_read(OUTPUT+128,1)==b'\0'
  return self.run('_Nt5VideoInitialize@4',(EXT,))
 def ioctl(self,code,input_size=4,output_size=80):
  self.u.mem_write(REQ,struct.pack('<6I',code,STATUS,INPUT,input_size,OUTPUT,output_size));self.put(STATUS,0xdead);self.put(STATUS+4,0xdead)
  assert self.run('_Nt5VideoStartIO@8',(EXT,REQ))==1
  return self.get(STATUS),self.get(STATUS+4)

m=Machine();assert m.run('_DriverEntry@8',(0x1111,0x2222))==0
assert struct.unpack_from('<I',m.init,4)[0]==5
results.append('Native 80-byte W2K initialization and required callbacks with stdcall ABI')
m=Machine();assert m.init_adapter()==1
# NTDDVDEO ioctl codes: device 0x23, METHOD_BUFFERED/FILE_ANY_ACCESS.
assert m.ioctl(0x230400)==(0,80)
mode=struct.unpack('<20I',m.u.mem_read(OUTPUT,80))
assert mode[:8]==(80,0,640,480,2560,1,32,60) and mode[13:16]==(0xff0000,0xff00,0xff)
results.append('Firmware NV2A mode is decoded into the native 32-bit RGB descriptor')
assert m.ioctl(0x230404)==(0,8)
assert struct.unpack('<2I',m.u.mem_read(OUTPUT,8))==(1,80)
results.append('One firmware mode is enumerated with correct output sizes')
for flags in [0,0x40000000,0x80000000,0xc0000000]:
 m.put(INPUT,flags);assert m.ioctl(0x23040c)==(0,0)
m.put(INPUT,1);assert m.ioctl(0x23040c)[0]==87
results.append('Mode zero accepts documented mapping flags and rejects unsupported modes')
m.put(INPUT,0);assert m.ioctl(0x230458,output_size=16)==(0,16)
assert m.calls[-1]==(0xf3c00000,0,0x400000,0)
assert struct.unpack('<4I',m.u.mem_read(OUTPUT,16))==(0x90000000,0x400000,0x90000000,640*480*4)
results.append('Framebuffer mapping uses the reserved GPU aperture and bounds the visible surface')
for code in [0x230400,0x230404,0x23040c,0x230458,0x23045c]:
 assert m.ioctl(code,input_size=0,output_size=0)[0]==122
assert m.ioctl(0x23ffff)[0]==1
results.append('Short buffers and unsupported controls return explicit errors')
for kwargs in [{'offset':0x100000},{'pitch':1280},{'format':2},{'width':2048}]:
 m=Machine(**kwargs);assert m.init_adapter()==0 and m.freed==[(EXT,MMIO)]
results.append('Invalid firmware mode or unreserved framebuffer fails and releases the register mapping')
m=Machine(map_status=8);assert m.init_adapter()==1;m.u.mem_write(OUTPUT,b'Z'*16)
assert m.ioctl(0x230458,output_size=16)==(8,0) and bytes(m.u.mem_read(OUTPUT,16))==b'Z'*16
results.append('VideoPort mapping failure propagates without publishing a bogus framebuffer')
report={'scope':__doc__,'miniport_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_imports_resolve':True,'tests':[{'test':x,'passed':True} for x in results]}
(out/'video-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(len(results),'video test groups passed')
