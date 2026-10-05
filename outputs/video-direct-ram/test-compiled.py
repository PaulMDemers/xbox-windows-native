"""Execute the diagnostic miniport with modeled VideoPort and physical geometry."""
import pathlib,sys,struct,json,hashlib,argparse
k=pathlib.Path(__file__).resolve().parent.parent/'native-windows-physical-f';old=k.parent/'native-windows-nt5-kernel';root=k.parents[1];sys.path.insert(0,str(root/'work/python-packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
ns={};text=(old/'test-boundary.py').read_text();exec(text[text.index('def symbols(p):'):text.index('sym=symbols(h)')],{'struct':struct},ns)
args=argparse.ArgumentParser();args.add_argument('--miniport',type=pathlib.Path,default=k.parent/'video-direct-ram/artifacts/xboxvnt5.sys');args.add_argument('--output',type=pathlib.Path,default=k.parent/'video-direct-ram/compiled-tests.json');args=args.parse_args()
path=args.miniport;pe=pefile.PE(str(path));sym=ns['symbols'](pe);base=pe.OPTIONAL_HEADER.ImageBase
for lib in pe.DIRECTORY_ENTRY_IMPORT:
 name=lib.dll.decode();folder=k/'package/F/winnt/system32';folder=folder/'drivers' if name.lower()=='videoprt.sys' else folder
 dll=pefile.PE(str(folder/name.lower()));exports={s.name for s in dll.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 assert all(i.name in exports for i in lib.imports),name
text=(old/'test-video.py').read_text();exec(text[text.index('STACK='):text.index('m=Machine();')])
class DiagnosticStop(Exception):pass
class Diagnostic(Machine):
 def __init__(self,height=480,range_status=0,initialize_status=0,register_map=True,small_aperture=False,**kw):
  self.small_aperture=small_aperture;self.range_status=range_status;self.initialize_status=initialize_status;self.register_map=register_map
  super().__init__(**kw);self.put(MMIO+0x680818,height-1)
 def KeBugCheckEx(self):
  self.failure=self.args(5);assert self.failure[0]==0xe0580001;raise DiagnosticStop(self.failure)
 def VideoPortGetAccessRanges(self):
  if self.range_status:self.ret(8,self.range_status)
  else:
   ptr=self.args(8)[4];super().VideoPortGetAccessRanges()
   if self.small_aperture:self.put(ptr+16+8,0x100000)
 def VideoPortGetDeviceBase(self):
  if self.register_map:super().VideoPortGetDeviceBase()
  else:self.ret(5,0)
 def VideoPortInitialize(self):
  super().VideoPortInitialize();self.u.reg_write(UC_X86_REG_EAX,self.initialize_status)
DRIVER=STACK+0x4000;DEXT=STACK+0x5000;IRP=STACK+0x6000;IOS=STACK+0x7000;RAW=STACK+0x8000;TRANSLATED=STACK+0x8100
ADD=STOP+0x800;PNP=STOP+0x820
class PnpMachine(Diagnostic):
 def __init__(self,add_status=0,pnp_status=0,**kwargs):
  super().__init__(**kwargs);self.add_status=add_status;self.pnp_status=pnp_status;self.forwarded=[]
  self.put(DRIVER+0x18,DEXT);self.put(DEXT+4,ADD);self.put(DRIVER+0xa4,PNP)
  self.put(IRP+0x60,IOS);self.put(IOS+4,RAW);self.put(IOS+8,TRANSLATED);self.put(RAW,1);self.put(TRANSLATED,1)
  self.hooks[ADD]=self.original_add;self.hooks[PNP]=self.original_pnp
 def original_add(self):self.forwarded.append(('add',self.args(2)));self.ret(2,self.add_status)
 def original_pnp(self):
  self.forwarded.append(('pnp',self.args(2)));self.u.mem_write(IRP,bytes(0x100));self.ret(2,self.pnp_status)
 def arm(self):
  assert self.run('_DriverEntry@8',(DRIVER,0x1234))==0
  assert self.get(DEXT+4)==sym['_XwnVideoAddDevice@8'] and self.get(DRIVER+0xa4)==sym['_XwnVideoPnp@8']
SEED=b'XWN-VID-TRACE01\n'+bytes(4080)
class TraceMachine(PnpMachine):
 def __init__(self,seed=SEED,open_status=0,write_status=0,**kwargs):
  self.seed=seed;self.open_status=open_status;self.write_status=write_status;self.saved=[];self.irql=0;self.closed=[]
  super().__init__(**kwargs)
 def HalGetBusDataByOffset(self):
  kind,bus,slot,buf,off,n=self.args(6);assert kind==4 and (bus,slot) in [(0,30),(1,0)] and off==0 and n==64
  self.u.mem_write(buf,bytes(64));self.ret(6,64)
 def KeGetCurrentIrql(self):self.ret(0,self.irql)
 def RtlInitUnicodeString(self):
  dst,src=self.args(2);i=0
  while self.u.mem_read(src+i,2)!=b'\0\0':i+=2
  assert self.u.mem_read(src,i).decode('utf-16le')==r'\SystemRoot\System32\xwn-video-trace.bin'
  self.u.mem_write(dst,struct.pack('<HHI',i,i+2,src));self.ret(2)
 def ZwCreateFile(self):
  handle,access,attrs,ios,size,flags,share,disp,options,ea,ealen=self.args(11)
  assert access==0x100003 and disp==1 and options==0x62 and share==1
  if not self.open_status:self.put(handle,0x4567)
  self.ret(11,self.open_status)
 def ZwQueryInformationFile(self):
  handle,ios,buf,n,cls=self.args(5);assert handle==0x4567 and cls==5
  self.u.mem_write(buf,struct.pack('<QQIBBxx',4096,len(self.seed),1,0,0));self.ret(5)
 def ZwReadFile(self):
  handle,event,apc,ctx,ios,buf,n,off,key=self.args(9);assert handle==0x4567 and n==4096 and self.get(off)==0
  self.u.mem_write(buf,self.seed);self.put(ios+4,len(self.seed));self.ret(9)
 def ZwWriteFile(self):
  handle,event,apc,ctx,ios,buf,n,off,key=self.args(9);assert handle==0x4567 and n==4096 and self.get(off)==0
  if not self.write_status:self.saved.append(bytes(self.u.mem_read(buf,n)));self.put(ios+4,n)
  self.ret(9,self.write_status)
 def ZwClose(self):self.closed.append(self.args(1)[0]);self.ret(1)
 def events(self):
  b=self.saved[-1];assert b[:16]==SEED[:16];return [e for i in range(struct.unpack_from('<I',b,16)[0]) if (e:=struct.unpack_from('<4I',b,32+i*16))[0] not in (8,9)]
results=[]
m=TraceMachine();m.arm();assert m.events()[0][0]==1
assert m.run('_XwnVideoAddDevice@8',(DRIVER,EXT))==0
m.u.mem_write(IOS+1,b'\x18');m.pnp_status=0xc00000bb
assert m.run('_XwnVideoPnp@8',(EXT,IRP))==0xc00000bb
assert [e[0] for e in m.events()]==[1,2,3,4,5];assert m.events()[-1]==(5,0x18,0xc00000bb,0)
results.append('Seeded bounded write-through trace captures AddDevice and optional PnP status without altering it')
m=TraceMachine();m.arm();assert m.run('_XwnVideoPnp@8',(EXT,IRP))==0
assert [e[0] for e in m.events()]==[1,4,7,5]
results.append('Trace mode forwards START after recording resource-list counts')
for kwargs,phase in [({'seed':b'BAD!'+SEED[4:]},4),({'seed':SEED[:2048]},2),({'open_status':0xc0000034},1),({'write_status':0xc0000185},5)]:
 m=TraceMachine(**kwargs)
 try:m.arm();raise AssertionError('Expected guard')
 except DiagnosticStop:assert m.failure[1:3]==(13,phase)
 assert not m.saved
results.append('Wrong marker, wrong size, missing file and write failures stop explicitly; no successful writes')
m=TraceMachine();m.arm();before=len(m.saved);m.irql=2;m.run('_XwnVideoTrace@16',(8,1,2,3));assert len(m.saved)==before
m.irql=0;m.run('_XwnVideoUnload@4',(DRIVER,));assert m.events()[-1][0]==6 and m.closed==[0x4567]
results.append('Elevated IRQL skips file IO; unload records and closes owned handle')
# A prior boot's records are discarded in RAM, without changing file open/read semantics.
m=TraceMachine(seed=SEED[:16]+bytes([0x55])*4080);m.arm()
assert m.events()[0][0]==1
assert struct.unpack_from('<I',m.saved[-1],16)[0]==18
assert m.saved[-1][-16:]==bytes(16)
results.append('Used trace accepted; record count restarts for this boot and stale tail is cleared')

# Execute the linked read-only observer against modeled non-PAE page tables/MSRs.
class MappingMachine(TraceMachine):
 def __init__(self,pae=False,features=0x11020,**kwargs):
  super().__init__(**kwargs);self.cpu_features=features;self.cpu_cr4=0x20 if pae else 0;self.msr_reads=[];self.pt_writes=[]
  self.u.mem_map(0xc0000000,0x400000)
  for va,pa in [(0x90000000,0xf3c00000),(0x903ff000,0xf3fff000),(0x83c00000,0x03c00000)]:
   self.put(0xc0300000+(va>>22)*4,0x01000003)
   self.put(0xc0000000+(va>>12)*4,pa|0x1b)
  regs=[UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBX,UC_X86_REG_ESP,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI]
  def cpu(u,a,size,ctx):
   op=bytes(u.mem_read(a,3))
   if op[:2]==b'\x0f\x20':
    assert op[2]&0xc0==0xc0
    cr=(op[2]>>3)&7;value={0:0x80010033,3:0x100000,4:self.cpu_cr4}[cr]
    u.reg_write(regs[op[2]&7],value);u.reg_write(UC_X86_REG_EIP,a+3)
   elif op[:2]==b'\x0f\xa2':
    assert u.reg_read(UC_X86_REG_EAX)==1
    u.reg_write(UC_X86_REG_EAX,0x683);u.reg_write(UC_X86_REG_EBX,0);u.reg_write(UC_X86_REG_ECX,0);u.reg_write(UC_X86_REG_EDX,self.cpu_features);u.reg_write(UC_X86_REG_EIP,a+2)
   elif op[:2]==b'\x0f\x32':
    msr=u.reg_read(UC_X86_REG_ECX);self.msr_reads.append(msr)
    assert msr in [0xfe,0x277,0x2ff]+list(range(0x200,0x210))
    value={0xfe:0x508,0x277:0x0007040600070406,0x2ff:0x806}.get(msr,0)
    u.reg_write(UC_X86_REG_EAX,value&0xffffffff);u.reg_write(UC_X86_REG_EDX,value>>32);u.reg_write(UC_X86_REG_EIP,a+2)
   elif op[:2] in [b'\x0f\x22',b'\x0f\x30',b'\x0f\x09']:
    raise AssertionError('Observer must not write CR/MSR or flush CPU caches')
  self.u.hook_add(UC_HOOK_CODE,cpu)
  self.u.hook_add(UC_HOOK_MEM_WRITE,lambda u,access,a,n,v,ctx:self.pt_writes.append(a) if 0xc0000000<=a<0xc0400000 else None)
 def records(self):
  b=self.saved[-1];return [struct.unpack_from('<4I',b,32+i*16) for i in range(struct.unpack_from('<I',b,16)[0])]
for pae,features in [(False,0x11020),(True,0x11020),(False,0)]:
 m=MappingMachine(pae,features);m.arm();m.run('_XwnVideoTraceMapping@16',(0x90000000,0xf3c00000,0x400000,0x3c00000))
 records=m.records();pages=[v for v in records if v[0]==0x24]
 assert len(pages)==(0 if pae else 4)
 if not pae:assert pages==[(0x24,0,0xf3c0001b,0),(0x24,1,0xf3fff01b,0),(0x24,2,0x03c0001b,0),(0x24,3,0,0)]
 assert len(m.msr_reads)==(20 if features else 0) and not m.pt_writes
results.append('Mapping observer reads present/nonpresent PTEs, skips PAE, gates/bounds MSRs, and never changes cache registers/page tables')
m=MappingMachine();m.arm();assert m.init_adapter()==1
assert m.ioctl(0x230458,output_size=16)==(0,16)
assert m.calls[-1]==(0x03c00000,0,0x400000,0)
assert any(v[0]==0x20 for v in m.records()) and not m.pt_writes
results.append('Successful mapping uses reserved RAM with original flags/ABI and appends observation records')
# Mapping lifecycle and geometry must remain intact for both supported RAM sizes.
for offset in [0x03c00000,0x07c00000]:
 m=MappingMachine(offset=offset);m.arm();assert m.init_adapter()==1
 assert m.ioctl(0x230458,output_size=16)==(0,16)
 assert m.calls[-1]==(offset,0,0x400000,0)
 assert struct.unpack('<4I',m.u.mem_read(OUTPUT,16))==(0x90000000,0x400000,0x90000000,640*480*4)
 assert m.ioctl(0x230400)==(0,80)
 mode=struct.unpack('<20I',m.u.mem_read(OUTPUT,80));assert mode[:8]==(80,0,640,480,2560,1,32,60)
 m.put(INPUT,0x90000000);assert m.ioctl(0x23045c)==(0,0);assert m.calls[-1]==(EXT,0x90000000,0)
 for code in [0x230400,0x230404,0x23040c,0x230458,0x23045c]:assert m.ioctl(code,input_size=0,output_size=0)[0]==122
for kwargs in [{'offset':0x100000},{'pitch':1280},{'format':2},{'width':2048}]:
 m=MappingMachine(**kwargs);m.arm()
 try:m.init_adapter();raise AssertionError('Expected geometry guard')
 except DiagnosticStop:assert m.failure[1] in [5,6]
m=MappingMachine(map_status=8);m.arm();assert m.init_adapter()==1;m.u.mem_write(OUTPUT,b'Z'*16)
try:m.ioctl(0x230458,output_size=16);raise AssertionError('Expected mapping guard')
except DiagnosticStop:assert m.failure[1:3]==(7,8)
assert bytes(m.u.mem_read(OUTPUT,16))==b'Z'*16
results.append('Both reserved RAM bases, unchanged mode and mapping/unmapping ABI, bad geometry/buffers and mapping failure publication checks pass')
r={'scope':'Compiled mapping observer with modeled NT file IO, page tables, CPUID, MSRs and PnP callbacks','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_imports_resolve':True,'passed':True,'tests':results}
args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
