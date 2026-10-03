"""Run built HAL boundary instructions and selected supplied-kernel paths.

Synthetic trap/PCR state; PIC end handler mocked. Stop BEFORE IRET. This is
not a guest boot, interrupt delivery, scheduler, or full hardware validation.
"""
import hashlib,json,pathlib,struct,sys
r=pathlib.Path(__file__).resolve().parents[2];out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(r/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
hp=out/'artifacts/halxboxnt5.dll'
kp=r/'outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe'
h=pefile.PE(str(hp));k=pefile.PE(str(kp))
def exports(p):return {x.name.decode():p.OPTIONAL_HEADER.ImageBase+x.address for x in p.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
hx,kx=exports(h),exports(k)
def symbols(p):
 data=p.__data__;pos=p.FILE_HEADER.PointerToSymbolTable;n=p.FILE_HEADER.NumberOfSymbols;strings=pos+18*n
 result={};i=0
 while i<n:
  raw,value,section,typ,cls,aux=struct.unpack_from('<8sIhHBB',data,pos+18*i)
  if raw[:4]==b'\0'*4:
   off=struct.unpack_from('<I',raw,4)[0];start=strings+off;name=data[start:data.find(b'\0',start)].decode('ascii')
  else:name=raw.rstrip(b'\0').decode('ascii')
  if section>0:result[name]=p.OPTIONAL_HEADER.ImageBase+p.sections[section-1].VirtualAddress+value
  i+=1+aux
 return result
sym=symbols(h)
STACK=0x800000;FRAME=STACK+0x9000;PCR=0xffdff000;PRCB=PCR+0x120;GDT=0x900000;STOP=0xa00000
REGS=[UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
DRS=[UC_X86_REG_DR0,UC_X86_REG_DR1,UC_X86_REG_DR2,UC_X86_REG_DR3,UC_X86_REG_DR6,UC_X86_REG_DR7]
results=[]
class Machine:
 def __init__(self):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);self.callbacks={};self.stopped=None;self.calls=[];u=self.u
  for p in (h,k):
   base=p.OPTIONAL_HEADER.ImageBase;u.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,p.get_memory_mapped_image())
  for a,size in [(STACK,0x10000),(PCR,0x4000),(0xffdf0000,0x1000),(GDT,0x1000),(STOP,0x1000)]:u.mem_map(a,size)
  def desc(base,access):return struct.pack('<HHBBBB',0xffff,base&65535,(base>>16)&255,access,0xcf,(base>>24)&255)
  u.mem_write(GDT+8,desc(0,0x9b));u.mem_write(GDT+16,desc(0,0x93));u.mem_write(GDT+32,desc(0,0xf3));u.mem_write(GDT+48,desc(PCR,0x93))
  u.reg_write(UC_X86_REG_GDTR,(0,GDT,0xff,0));u.reg_write(UC_X86_REG_CS,8)
  for reg in [UC_X86_REG_DS,UC_X86_REG_ES,UC_X86_REG_SS,UC_X86_REG_GS]:u.reg_write(reg,16)
  u.reg_write(UC_X86_REG_FS,48)
  self.put(PCR+0x1c,PCR);self.put(PCR+0x20,PRCB);self.put(PCR,0x12345678)
  u.reg_write(UC_X86_REG_EFLAGS,2)
  # Bind actual HAL imports to the supplied kernel. Unused imports may be data.
  for lib in h.DIRECTORY_ENTRY_IMPORT:
   for x in lib.imports:self.put(x.address,kx[x.name.decode()])
  for lib in k.DIRECTORY_ENTRY_IMPORT:
   for x in lib.imports:
    if lib.dll.lower()==b'hal.dll' and x.name.decode() in hx:self.put(x.address,hx[x.name.decode()])
  self.callbacks[STOP]=lambda:self.stop('return')
  u.hook_add(UC_HOOK_CODE,self.hook)
 def get(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def reg(self,n):return self.u.reg_read(n)
 def stop(self,why):self.stopped=why;self.u.emu_stop()
 def hook(self,u,a,size,ctx):
  if a in self.callbacks:self.callbacks[a]();return
  if bytes(u.mem_read(a,size))==b'\xcf':self.stop('before_iret')
 def ret(self,n=0):
  sp=self.reg(UC_X86_REG_ESP);ip=self.get(sp);self.u.reg_write(UC_X86_REG_ESP,sp+4+n);self.u.reg_write(UC_X86_REG_EIP,ip)
 def run(self,name,cx=FRAME,dx=0,args=(),ebp=0x11223344,hardware=False):
  u=self.u;sp=FRAME+0x68 if hardware else STACK+0x7000
  for i,v in enumerate((0xb00000,8,0x202) if hardware else (STOP,*args)):self.put(sp+4*i,v)
  for reg,v in zip(REGS,[0x101,0x202,0x303,0x404,0x505,0x606,ebp]):u.reg_write(reg,v)
  u.reg_write(UC_X86_REG_ESP,sp);u.reg_write(UC_X86_REG_ECX,cx);u.reg_write(UC_X86_REG_EDX,dx)
  u.emu_start(sym.get(name,hx.get(name,0)),0,count=20000)
  assert self.stopped,'Instruction budget exhausted'
 def frame(self,cs=8,flags=0x202):
  for off,val in [(0x30,16),(0x34,16),(0x38,16),(0x3c,0x303),(0x40,0x202),(0x44,0x101),(0x4c,0x12345678),(0x50,48),(0x54,0x606),(0x58,0x505),(0x5c,0x404),(0x60,0x707),(0x64,0),(0x68,0xb00000),(0x6c,cs),(0x70,flags)]:self.put(FRAME+off,val)
def passed(name):results.append({'test':name,'passed':True})

m=Machine();m.frame();original=bytes(m.u.mem_read(FRAME,140))
m.callbacks[kx['Kei386EoiHelper']]=lambda:m.stop('eoi_boundary')
m.run('@HalpNt5Eoi@4')
assert m.stopped=='eoi_boundary' and m.reg(UC_X86_REG_ESP)==FRAME and m.reg(UC_X86_REG_EBP)==FRAME
assert bytes(m.u.mem_read(FRAME,140))==original
passed('EOI adapter discards C stack, installs ESP/EBP trap pointer and preserves frame')

for old in [0,1,2,27]:
 m=Machine();m.frame();m.callbacks[kx['KeUpdateSystemTime']]=lambda:m.stop('time_boundary')
 m.run('@HalpNt5UpdateSystemTime@12',dx=100144,args=(old,))
 assert m.stopped=='time_boundary' and m.reg(UC_X86_REG_EAX)==100144 and m.reg(UC_X86_REG_EBP)==FRAME
 assert m.reg(UC_X86_REG_ESP)==FRAME-8 and [m.get(FRAME-8),m.get(FRAME-4)]==[old,0x30]
passed('Clock adapter supplies EAX increment and native old-IRQL/vector stack for four levels')

m=Machine();m.frame()
def end():
 sp=m.reg(UC_X86_REG_ESP);m.calls.append((m.get(sp+4),m.get(sp+8)));m.ret(8)
m.callbacks[sym['_HalEndSystemInterrupt@8']]=end
m.run('HalEndSystemInterrupt',args=(2,0x30),ebp=FRAME)
assert m.calls==[(2,FRAME)] and m.reg(UC_X86_REG_ESP)==STACK+0x700c and m.reg(UC_X86_REG_EBP)==FRAME
passed('Public interrupt-end translates native vector argument to EBP frame and cleans 8 bytes')

m=Machine()
def dispatch():
 for reg in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]:m.u.reg_write(reg,0xbad)
 m.ret()
m.callbacks[kx['KiDispatchInterrupt']]=dispatch
m.run('_HalpNt5DispatchInterrupt@0')
assert [m.reg(x) for x in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]]==[0x404,0x505,0x606,0x11223344]
passed('DPC wrapper preserves C nonvolatile registers despite native-helper clobbers')

for cs,flags,active,save in [(8,0x202,1,False),(0x1b,0x202,0,False),(0x1b,0x202,1,True),(0,0x20202,1,True)]:
 m=Machine();m.frame(cs,flags);m.u.mem_write(PCR+0x50,bytes([active]));m.put(FRAME+0x2c,0xdead)
 user=[0x1110,0x2220,0x3330,0x4440,0xffff0ff0,0x401];kernel=[0x5550,0x6660,0x7770,0x8880,0xffff0ff0,0x400]
 for reg,v in zip(DRS,user):m.u.reg_write(reg,v)
 for i,v in enumerate(kernel):m.put(PRCB+0x2f8+4*i,v)
 m.run('@HalpNt5EnterInterruptTrap@4')
 assert m.get(PCR)==0xffffffff and m.get(FRAME+0x4c)==0x12345678
 if save:
  assert [m.get(FRAME+0x18+4*i) for i in range(6)]==user
  assert [m.reg(x) for x in DRS]==kernel
 else:assert m.get(FRAME+0x2c)==0 and [m.reg(x) for x in DRS]==user
passed('Trap entry handles kernel, user debug-off, user debug-on and V86 register-save cases')

m=Machine();m.frame();m.run('@HalpNt5Eoi@4')
assert m.stopped=='before_iret' and m.reg(UC_X86_REG_ESP)==FRAME+0x68
assert [m.reg(x) for x in REGS]==[0x101,0x202,0x303,0x404,0x505,0x606,0x707]
assert m.get(PCR)==0x12345678
passed('Actual installed NT5 EOI restores registers and exception chain up to IRET, kernel mode')

# These data RVAs are pinned to the exact installed kernel and captured in the
# accompanying disassembly. Select the no-tick-rollover, empty timer-list path.
assert hashlib.sha256(kp.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
m=Machine();m.frame();m.put(0x46cb98,200000);m.put(0x46cb84,0);m.put(0x480c00,0x480c00)
m.put(0xffdf0008,0xfffffff0);m.put(0xffdf000c,5);m.put(0xffdf0010,5)
def timer_end():
 sp=m.reg(UC_X86_REG_ESP);m.calls.append((m.get(sp+4),m.get(sp+8)));m.ret(8)
m.callbacks[sym['_HalEndSystemInterrupt@8']]=timer_end
m.run('@HalpNt5UpdateSystemTime@12',dx=100144,args=(2,))
assert m.stopped=='before_iret' and m.calls==[(2,FRAME)]
assert [m.get(0xffdf0008),m.get(0xffdf000c),m.get(0xffdf0010)]==[100128,6,6]
assert m.get(0x46cb98)==99856 and m.reg(UC_X86_REG_ESP)==FRAME+0x68
assert [m.reg(x) for x in REGS]==[0x101,0x202,0x303,0x404,0x505,0x606,0x707]
passed('Actual NT5 timer consumes increment, handles 64-bit carry, calls adapter and reaches EOI')

for accepted in [False,True]:
 m=Machine();m.put(0x46cb98,200000);m.put(0x46cb84,0);m.put(0x480c00,0x480c00)
 m.put(sym['_HalpCurrentTimeIncrement'],100144);m.put(sym['_HalpCurrentRollOver'],11949)
 def begin():
  sp=m.reg(UC_X86_REG_ESP)
  assert [m.get(sp+4),m.get(sp+8)]==[28,0x30]
  m.put(m.get(sp+12),2);m.u.reg_write(UC_X86_REG_EAX,int(accepted));m.ret(12)
 def finish():
  sp=m.reg(UC_X86_REG_ESP);m.calls.append((m.get(sp+4),m.get(sp+8)));m.ret(8)
 m.callbacks[hx['HalBeginSystemInterrupt']]=begin
 m.callbacks[sym['_HalEndSystemInterrupt@8']]=finish
 m.run('_HalpClockInterrupt',cx=0x202,dx=0x303,ebp=0x707,hardware=True)
 assert m.stopped=='before_iret' and m.reg(UC_X86_REG_ESP)==FRAME+0x68
 assert [m.reg(x) for x in REGS]==[0x101,0x202,0x303,0x404,0x505,0x606,0x707]
 assert m.get(PCR)==0x12345678
 assert m.get(sym['_HalpPerfCounter'])==(11949 if accepted else 0)
 assert m.get(0xffdf0008)==(100144 if accepted else 0)
 assert m.calls==([(2,FRAME)] if accepted else [])
passed('Built IRQ0 entry and clock handler reach native EOI for accepted and spurious interrupts')

report={'hal_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'kernel_sha256':hashlib.sha256(kp.read_bytes()).hexdigest(),
 'scope':__doc__,'tests':results}
(out/'boundary-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))


