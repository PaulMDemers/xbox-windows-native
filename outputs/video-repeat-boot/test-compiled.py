"""Execute the diagnostic miniport with modeled VideoPort and physical geometry."""
import pathlib,sys,struct,json,hashlib,argparse
k=pathlib.Path(__file__).resolve().parent.parent/'native-windows-physical-f';old=k.parent/'native-windows-nt5-kernel';root=k.parents[1];sys.path.insert(0,str(root/'work/python-packages'))
import pefile
from unicorn import *
from unicorn.x86_const import *
ns={};text=(old/'test-boundary.py').read_text();exec(text[text.index('def symbols(p):'):text.index('sym=symbols(h)')],{'struct':struct},ns)
args=argparse.ArgumentParser();args.add_argument('--miniport',type=pathlib.Path,default=k.parent/'video-repeat-boot/artifacts/xboxvnt5.sys');args.add_argument('--output',type=pathlib.Path,default=k.parent/'video-repeat-boot/compiled-tests.json');args=args.parse_args()
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
 def __init__(self,add_status=0,pnp_status=0):
  super().__init__();self.add_status=add_status;self.pnp_status=pnp_status;self.forwarded=[]
  self.put(DRIVER+0x18,DEXT);self.put(DEXT+4,ADD);self.put(DRIVER+0xa4,PNP)
  self.put(IRP+0x60,IOS);self.put(IOS+4,RAW);self.put(IOS+8,TRANSLATED);self.put(RAW,1);self.put(TRANSLATED,1)
  self.hooks[ADD]=self.original_add;self.hooks[PNP]=self.original_pnp
 def original_add(self):self.forwarded.append(('add',self.args(2)));self.ret(2,self.add_status)
 def original_pnp(self):
  self.forwarded.append(('pnp',self.args(2)));self.u.mem_write(IRP,bytes(0x100));self.ret(2,self.pnp_status)
 def arm(self):
  assert self.run('_DriverEntry@8',(DRIVER,0x1234))==0
  assert self.get(DEXT+4)==sym['_XwnVideoAddDevice@8'] and self.get(DRIVER+0xa4)==sym['_XwnVideoPnp@8']

results=[]
for status in [0,0x103,0xc000000e,0xc00000bb]:
 m=PnpMachine(pnp_status=status);m.arm()
 assert m.run('_XwnVideoAddDevice@8',(DRIVER,EXT))==0
 assert m.run('_XwnVideoPnp@8',(EXT,IRP))==status
 assert m.forwarded==[('add',(DRIVER,EXT)),('pnp',(EXT,IRP))]
results.append('START forwards once and preserves success/pending/failure status without reading completed IRP')
m=PnpMachine();m.arm();m.put(DRIVER+0xa4,PNP)
assert m.run('_XwnVideoAddDevice@8',(DRIVER,EXT))==0
assert m.get(DRIVER+0xa4)==sym['_XwnVideoPnp@8']
results.append('AddDevice rewraps a VideoPort-installed dispatch')
m=PnpMachine(add_status=0xc000009a);m.arm()
try:m.run('_XwnVideoAddDevice@8',(DRIVER,EXT));raise AssertionError('Expected original failure guard')
except DiagnosticStop:assert m.failure==(0xe0580001,10,0xc000009a,EXT,0)
results.append('Existing failure diagnostics preserved')
imports={lib.dll.decode():[i.name.decode() for i in lib.imports] for lib in pe.DIRECTORY_ENTRY_IMPORT}
flat={i for names in imports.values() for i in names}
assert not any(name.startswith('Zw') for name in flat)
assert 'HalGetBusDataByOffset' not in flat
assert b'XWN-VID-TRACE01' not in path.read_bytes()
results.append('No Zw file I/O imports, trace-file marker, or diagnostic PCI-read import')
r=dict(scope='Compiled x86 miniport callbacks with modeled NT5 imports; not a guest boot',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),passed=True,imports=imports,tests=results)
args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
