"""Execute the diagnostic miniport with modeled VideoPort and physical geometry."""
import pathlib,sys,struct,json,hashlib
k=pathlib.Path(__file__).resolve().parent;old=k.parent/'native-windows-nt5-kernel';root=k.parents[1];sys.path.insert(0,str(root/'work/python-packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
ns={};text=(old/'test-boundary.py').read_text();exec(text[text.index('def symbols(p):'):text.index('sym=symbols(h)')],{'struct':struct},ns)
path=k/'artifacts/xboxvnt5-diagnostic.sys';pe=pefile.PE(str(path));sym=ns['symbols'](pe);base=pe.OPTIONAL_HEADER.ImageBase
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
results=[]
for width,height,pitch in [(640,480,2560),(1024,576,4096)]:
 m=Diagnostic(width=width,height=height,pitch=pitch);assert m.run('_DriverEntry@8',(1,2))==0;assert m.init_adapter()==1
 assert m.ioctl(0x230400)==(0,80);mode=struct.unpack('<20I',m.u.mem_read(OUTPUT,80));assert mode[:8]==(80,0,width,height,pitch,1,32,60)
 m.put(INPUT,0);assert m.ioctl(0x230458,output_size=16)==(0,16);assert m.calls[-1]==(0xf3c00000,0,0x400000,0)
 results.append({'mode':[width,height,pitch],'initialized_and_mapped':True})
for stage,kw in [(1,{'initialize_status':0xc000000e}),(2,{'range_status':55}),(3,{'small_aperture':True}),(4,{'register_map':False}),(5,{'format':2}),(6,{'offset':0x100000}),(7,{'map_status':8})]:
 m=Diagnostic(**kw)
 try:
  if stage==1:m.run('_DriverEntry@8',(1,2))
  else:
   m.init_adapter()
   if stage==7:m.ioctl(0x230458,output_size=16)
  raise AssertionError('Expected diagnostic stop')
 except DiagnosticStop:
  assert m.failure[1]==stage;results.append({'stage':stage,'bugcheck':[hex(v) for v in m.failure]})
r={'scope':__doc__,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_imports_resolve':True,'tests':results}
(k/'video-diagnostic-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
