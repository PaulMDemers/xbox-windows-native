"""Execute the built loader's NTFS read code against modeled disk I/O and extent lookup."""
import pathlib,sys,json,struct,hashlib
out=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(out.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
path=out/'artifacts/autorun-006/freeldr_pe.exe';pe=pefile.PE(str(path));base=pe.OPTIONAL_HEADER.ImageBase
sym=json.loads((out/'ntfs-functions.json').read_text());exports={s.name.decode():base+s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
VOL=0x800000;FILE=VOL+0x1000;FIRST=VOL+0x2000;SECOND=VOL+0x3000;BUFFER=VOL+0x4000;COUNT=VOL+0x8000;STACK=VOL+0x10000;STOP=VOL+0x1f000
class Machine:
 def __init__(self,missing=False,short=False):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);u=self.u;u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(VOL,0x20000)
  self.missing=missing;self.short=short;self.lookups=[];self.frees=[];self.disk=bytearray(40*2048);self.payload=bytes((i*37+(i>>8))&255 for i in range(8192));self.disk[10*2048:12*2048]=self.payload[:4096];self.disk[30*2048:32*2048]=self.payload[4096:]
  self.put(VOL+512,2048);u.mem_write(VOL+11,struct.pack('<H',512));self.put(VOL+532,7);self.put(VOL+536,VOL+0x9000)
  self.put(FILE,VOL);self.put(FILE+4,FIRST);u.mem_write(FILE+8,struct.pack('<Q',123));self.context(FIRST,0,1,10,8192);self.context(SECOND,2,3,30,0)
  self.hooks={STOP:self.stop,exports['FsGetDeviceSpecific']:lambda:self.ret(FILE),exports['ArcRead']:self.read,exports['ArcSeek']:self.seek,exports['DbgPrint']:lambda:self.ret(0),exports['DbgPrint2']:lambda:self.ret(0),exports['FrLdrTempFree']:self.free,sym['_NtfsFindAttributeAtVCN']:self.find}
  u.hook_add(UC_HOOK_CODE,lambda u,a,z,c:self.hooks[a]() if a in self.hooks else None)
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v))
 def get(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(self,result=0):
  sp=self.u.reg_read(UC_X86_REG_ESP);self.u.reg_write(UC_X86_REG_EAX,result);self.u.reg_write(UC_X86_REG_EIP,self.get(sp));self.u.reg_write(UC_X86_REG_ESP,sp+4)
 def stop(self):self.stopped=True;self.u.emu_stop()
 def context(self,p,low,high,lcn,size):
  a=p+48;self.put(a,0x80);self.put(a+4,72);self.u.mem_write(a+8,b'\1');self.u.mem_write(a+16,struct.pack('<QQH',low,high,64));self.u.mem_write(a+48,struct.pack('<Q',size));self.u.mem_write(a+64,bytes([0x11,2,lcn,0]))
 def seek(self):
  dev,p,mode=self.args(3);assert dev==7 and mode==0;self.position=struct.unpack('<Q',self.u.mem_read(p,8))[0];self.ret(0)
 def read(self):
  dev,p,n,count=self.args(4);assert dev==7;amount=n-1 if self.short else n;self.u.mem_write(p,bytes(self.disk[self.position:self.position+amount]));self.put(count,amount);self.position+=amount;self.ret(0)
 def find(self):
  assert self.u.reg_read(UC_X86_REG_EAX)==VOL
  lo,hi,typ,name,vcn,vhi=self.args(6);assert (lo,hi,typ,vhi)==(123,0,0x80,0);self.lookups.append(vcn);self.ret(0 if self.missing else SECOND)
 def free(self):self.frees.append(self.args(2)[0]);self.ret(0)
 def run(self,offset,n):
  self.stopped=False;self.u.mem_write(FILE+16,struct.pack('<Q',offset));self.u.mem_write(BUFFER,b'\xcc'*0x4000);sp=STACK+0xe000
  self.u.mem_write(sp,struct.pack('<5I',STOP,1,BUFFER,n,COUNT));self.u.reg_write(UC_X86_REG_ESP,sp);self.u.emu_start(sym['_NtfsRead'],0,count=400000)
  assert self.stopped;return self.u.reg_read(UC_X86_REG_EAX),self.get(COUNT),bytes(self.u.mem_read(BUFFER,self.get(COUNT)))
results=[]
m=Machine();r,n,data=m.run(0,8192);assert (r,n,data)==(0,8192,m.payload) and m.lookups==[2] and m.frees==[SECOND];results.append('Complete read spanning two separately located DATA extents')
m=Machine();r,n,data=m.run(3072,4096);assert (r,n,data)==(0,4096,m.payload[3072:7168]);results.append('Unaligned request crosses the extent boundary without losing or repeating bytes')
m=Machine();r,n,data=m.run(7168,8192);assert (r,n,data)==(0,1024,m.payload[7168:]);results.append('Seek into later extent and clamp request at logical EOF')
m=Machine();assert m.run(8192,128)[:2]==(0,0);assert m.run(0,0)[:2]==(0,0);results.append('EOF and zero-byte reads do not access disk')
m=Machine(missing=True);r,n,data=m.run(0,8192);assert r!=0 and n==4096 and data==m.payload[:4096];results.append('Missing later extent reports I/O failure with the actual partial count')
m=Machine(short=True);r,n,data=m.run(0,8192);assert r!=0 and n==0;results.append('Short underlying disk transfer is rejected')
report={'scope':__doc__,'loader_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'passed':len(results),'tests':results,'limitation':'Extent lookup is modeled; real ATTRIBUTE_LIST lookup is separately exercised by the unchanged fragmented SYSTEM hive in xemu run 051.'}
(out/'ntfs-extent-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
