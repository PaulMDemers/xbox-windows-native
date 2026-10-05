"""Execute rebuilt display callbacks with injected engine/miniport failures."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
p=k/'artifacts/framebuf.dll';pe=pefile.PE(str(p));base=pe.OPTIONAL_HEADER.ImageBase
ns={};s=(ws/'outputs/native-windows-nt5-kernel/test-boundary.py').read_text()
exec(s[s.index('def symbols(p):'):s.index('sym=symbols(h)')],{'struct':struct},ns)
symbol_pe=pefile.PE(str(k/'artifacts/framebuf-symbols.dll'))
assert symbol_pe.OPTIONAL_HEADER.ImageBase==base and symbol_pe.OPTIONAL_HEADER.AddressOfEntryPoint==pe.OPTIONAL_HEADER.AddressOfEntryPoint
for sec in pe.sections:
 original=next(v for v in symbol_pe.sections if v.VirtualAddress==sec.VirtualAddress)
 assert sec.Characteristics==original.Characteristics
 assert sec.get_data()[:sec.Misc_VirtualSize]==original.get_data()[:sec.Misc_VirtualSize]
sym=ns['symbols'](symbol_pe)
engine=pefile.PE(str(ws/'outputs/native-windows-physical-f/package/F/winnt/system32/win32k.sys'))
exports={e.name for e in engine.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
assert all(i.name in exports for lib in pe.DIRECTORY_ENTRY_IMPORT for i in lib.imports)
STACK=0x1000000;DEV=STACK+0x1000;STOP=0x1100000
class Machine:
 def __init__(self,mode_fail=False,map_fail=False,bitmap_fail=False,associate_fail=False,delete_fail=False,unmap_fail=False,bpp=32):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);self.calls=[];self.options=locals().copy();self.stopped=False
  for a,n in [(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),(STACK,0x10000),(STOP,0x1000)]:self.u.mem_map(a,n)
  self.u.mem_write(base,pe.get_memory_mapped_image());self.hooks={STOP:self.stop}
  for off,val in [(0,0x1234),(4,0x2345),(16,1024),(20,576),(24,4096),(28,bpp)]:self.put(DEV+off,val)
  index=1
  for lib in pe.DIRECTORY_ENTRY_IMPORT:
   for imp in lib.imports:
    addr=STOP+index*16;index+=1;self.put(imp.address,addr)
    self.hooks[addr]=getattr(self,imp.name.decode(),self.unexpected)
  self.u.hook_add(UC_HOOK_CODE,lambda u,a,n,c:self.hooks[a]() if a in self.hooks else None)
 def get(self,p):return struct.unpack('<I',self.u.mem_read(p,4))[0]
 def put(self,p,v):self.u.mem_write(p,struct.pack('<I',v&0xffffffff))
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.u.reg_read(UC_X86_REG_ESP)+4,4*n))
 def ret(self,n,value=0):
  sp=self.u.reg_read(UC_X86_REG_ESP);ip=self.get(sp);self.u.reg_write(UC_X86_REG_EAX,value);self.u.reg_write(UC_X86_REG_ESP,sp+4+4*n);self.u.reg_write(UC_X86_REG_EIP,ip)
 def stop(self):self.stopped=True;self.u.emu_stop()
 def unexpected(self):
  ip=self.u.reg_read(UC_X86_REG_EIP);imports=[i.name.decode() for lib in pe.DIRECTORY_ENTRY_IMPORT for i in lib.imports];raise AssertionError('Unexpected imported engine call: '+imports[(ip-STOP)//16-1])
 def run(self,name):
  sp=STACK+0xf000;self.put(sp,STOP);self.put(sp+4,DEV);self.u.reg_write(UC_X86_REG_ESP,sp);self.stopped=False
  self.u.emu_start(sym[name],0,count=100000)
  assert self.stopped and self.u.reg_read(UC_X86_REG_ESP)==sp+8
  return self.u.reg_read(UC_X86_REG_EAX)
 def EngDeviceIoControl(self):
  driver,code,inp,ni,out,no,ret=self.args(7);assert driver==0x1234
  if code==0x23040c:self.calls.append('mode');status=int(self.options['mode_fail'])
  elif code==0x230458:
   self.calls.append('map');assert ni==4 and no==16 and self.get(inp)==0
   status=int(self.options['map_fail'])
   if not status:self.u.mem_write(out,struct.pack('<4I',0x90000000,0x400000,0x90001000,1024*576*4))
  elif code==0x23045c:
   assert ni==4 and self.get(inp)==0x90000000
   self.calls.append('unmap');status=int(self.options['unmap_fail'])
  else:raise AssertionError(hex(code))
  self.put(ret,0);self.ret(7,status)
 def EngCreateBitmap(self):
  assert self.args(6)==(1024,576,4096,6,1,0x90001000)
  self.calls.append('bitmap');self.ret(6,0 if self.options['bitmap_fail'] else 0x3344)
 def EngAssociateSurface(self):
  assert self.args(3)==(0x3344,0x2345,0);self.calls.append('associate');self.ret(3,not self.options['associate_fail'])
 def EngDeleteSurface(self):
  assert self.args(1)==(0x3344,);self.calls.append('delete');self.ret(1,not self.options['delete_fail'])
 def EngFreeMem(self):
  assert self.args(1)==(DEV,);self.calls.append('free_pdev');self.ret(1)
 def clear(self):return self.get(DEV+8)==self.get(DEV+48)==self.get(DEV+52)==0
results=[]
for option,expected in [('mode_fail',['mode']),('map_fail',['mode','map']),('bitmap_fail',['mode','map','bitmap','unmap']),('associate_fail',['mode','map','bitmap','associate','delete','unmap'])]:
 m=Machine(**{option:True});assert m.run('_DrvEnableSurface@4')==0;assert m.calls==expected and m.clear(),(option,m.calls)
 m.run('_DrvDisablePDEV@4');assert m.calls==expected+['free_pdev']
results.append('Mode/map failures publish nothing; bitmap/association failures release the acquired mapping before PDEV free')
m=Machine(bpp=7);assert m.run('_DrvEnableSurface@4')==0 and m.calls==['mode','map','unmap'] and m.clear()
results.append('Unsupported bitmap format unwinds its mapping')
m=Machine();assert m.run('_DrvEnableSurface@4')==0x3344;assert m.get(DEV+48)==0x90001000 and m.get(DEV+52)==0x90000000
n=len(m.calls);assert m.run('_DrvEnableSurface@4')==0 and len(m.calls)==n
m.run('_DrvDisableSurface@4');assert m.calls[-2:]==['delete','unmap'] and m.clear()
n=len(m.calls);m.run('_DrvDisableSurface@4');assert len(m.calls)==n
m.run('_DrvDisablePDEV@4');assert m.calls[-1]=='free_pdev'
results.append('Mapping base distinct from visible base is used for unmap; delete precedes unmap, duplicate enable is rejected and repeated disable is harmless')
m=Machine(bitmap_fail=True,unmap_fail=True);assert m.run('_DrvEnableSurface@4')==0
assert m.get(DEV+52)==0x90000000;n=len(m.calls);assert m.run('_DrvEnableSurface@4')==0 and len(m.calls)==n
m.run('_DrvDisablePDEV@4');assert m.calls[-1]=='unmap' and 'free_pdev' not in m.calls
m.options['unmap_fail']=False;m.run('_DrvDisablePDEV@4');assert m.calls[-2:]==['unmap','free_pdev'] and m.clear()
results.append('Failed unmap retains ownership, blocks remap and retries during PDEV teardown; persistent failure does not free its owner')
for association in [False,True]:
 m=Machine(associate_fail=association,delete_fail=True)
 assert m.run('_DrvEnableSurface@4')==(0 if association else 0x3344)
 m.run('_DrvDisablePDEV@4');assert m.get(DEV+8)==0x3344 and 'unmap' not in m.calls and 'free_pdev' not in m.calls
 m.options['delete_fail']=False;m.run('_DrvDisablePDEV@4');assert m.calls[-3:]==['delete','unmap','free_pdev'] and m.clear()
results.append('Failed engine deletion never unmaps a live surface or frees its owner; successful retry releases in order')
r=dict(scope=__doc__,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all_imports_resolve=True,passed=True,tests=results,limits='Modeled callbacks with compiled x86 code, not live GDI concurrency or PnP stop/remove qualification. A persistent release error can retain resources until teardown/reboot; no arbitrary forced unmap.')
(k/'compiled-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
