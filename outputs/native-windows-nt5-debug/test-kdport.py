"""Execute the built debugger exports and cportlib instructions with UART I/O
modeled through Unicorn IN/OUT hooks. No kernel debugger or real UART attached.
"""
import pathlib
KD_SCOPE=__doc__
test_file=pathlib.Path(__file__).resolve()
# Reuse the PE mapper and symbol reader, without running that file's tests.
exec((test_file.parent/'test-boundary.py').read_text().split('m=Machine();m.frame();original=')[0])
from unicorn import UC_HOOK_INSN
from collections import deque
PARAM=STACK+0x1000;BYTE=PARAM+32
class UART:
 def __init__(self,base):
  self.base=base;self.reg=[0]*8;self.rx=deque();self.tx=[];self.dll=0;self.dlm=0
  self.errors=0;self.lsr_reads=0;self.arrive_at=None;self.tx_ready_at=0
 def read(self,n):
  if n==0:
   if self.reg[3]&0x80:return self.dll
   return self.rx.popleft() if self.rx else 0
  if n==1 and self.reg[3]&0x80:return self.dlm
  if n==5:
   self.lsr_reads+=1
   if self.arrive_at==self.lsr_reads:self.rx.append(0x42)
   return (0x60 if self.lsr_reads>=self.tx_ready_at else 0)|(1 if self.rx else 0)|self.errors
  if n==6:
   if self.reg[4]&0x10:
    m=self.reg[4];return ((m&1)<<5)|((m&2)<<3)|((m&4)<<4)|((m&8)<<4)
   return 0xb0
  return self.reg[n]
 def write(self,n,value):
  if n==0:
   if self.reg[3]&0x80:self.dll=value
   else:self.tx.append(value)
  elif n==1 and self.reg[3]&0x80:self.dlm=value
  else:self.reg[n]=value

class SerialMachine(Machine):
 def __init__(self,ports=()):
  super().__init__();self.ports={n:UART(n) for n in ports};self.io=[];self.io_count=0
  self.u.hook_add(UC_HOOK_INSN,self.read_port,None,1,0,UC_X86_INS_IN)
  self.u.hook_add(UC_HOOK_INSN,self.write_port,None,1,0,UC_X86_INS_OUT)
 def trace(self,item):
  self.io_count+=1
  if len(self.io)<1000:self.io.append(item)
 def read_port(self,u,port,size,ctx):
  assert size==1;self.trace(('in',port))
  for base,p in self.ports.items():
   if base<=port<base+8:return p.read(port-base)
  return 255
 def write_port(self,u,port,size,value,ctx):
  assert size==1;self.trace(('out',port,value))
  for base,p in self.ports.items():
   if base<=port<base+8:p.write(port-base,value);return
 def call(self,name,*args,limit=20000):
  self.stopped=None;sp=STACK+0x7000
  for i,v in enumerate((STOP,*args)):self.put(sp+i*4,v)
  preserved={UC_X86_REG_EBX:0x444,UC_X86_REG_ESI:0x555,UC_X86_REG_EDI:0x666,UC_X86_REG_EBP:0x777}
  for reg,v in preserved.items():self.u.reg_write(reg,v)
  self.u.reg_write(UC_X86_REG_ESP,sp);self.u.emu_start(hx[name],0,count=limit)
  assert self.stopped=='return',name+' failed to return within instruction budget'
  assert self.reg(UC_X86_REG_ESP)==sp+4*(len(args)+1),name+' wrong stack cleanup'
  assert all(self.reg(reg)==v for reg,v in preserved.items()),name+' clobbered nonvolatile register'
  return self.reg(UC_X86_REG_EAX)
 def init(self,com=1,baud=19200,initialize=1):
  self.put(PARAM,com);self.put(PARAM+4,baud)
  return self.call('KdPortInitialize',PARAM,0,initialize)&255

results=[]
m=SerialMachine();m.u.mem_write(BYTE,b'Q')
assert m.call('KdPortGetByte',BYTE)==1 and m.call('KdPortPollByte',BYTE)==1
m.call('KdPortPutByte',65);assert m.io_count==0 and m.u.mem_read(BYTE,1)==b'Q'
assert m.call('KdPortGetByte',0)==2 and m.call('KdPortPollByte',0)==2
passed('Uninitialized reads return no-data, null output returns error, early transmit performs no I/O')

for com,baud in [(5,19200),(1,115201),(1,56000),(1,1)]:
 m=SerialMachine((0x3f8,));assert m.init(com,baud)==0 and m.io_count==0
m=SerialMachine();assert m.init(0,0)==0 and m.get(hx['KdComPortInUse'])==0
assert set(item[1]&~7 for item in m.io)=={0x2f8,0x3f8}
passed('Invalid selections/rates rejected without I/O; missing UARTs fail discovery')

m=SerialMachine((0x3f8,));assert m.init(1,38400,0)==1
assert m.get(hx['KdComPortInUse'])==0 and m.call('KdPortPollByte',BYTE)==1
# Selection persists across the later activation call as in native NT5.
assert m.init(2,9600,1)==1;p=m.ports[0x3f8]
assert (p.dll,p.dlm,p.reg[1],p.reg[3],p.reg[4],p.reg[2])==(3,0,0,3,11,7)
assert m.get(hx['KdComPortInUse'])==0x3f8
passed('Discovery/activation phases preserve selection and configure 38400 baud, 8N1, FIFO, interrupts off')

for ports,expected in [((0x2f8,0x3f8),0x2f8),((0x3f8,),0x3f8)]:
 m=SerialMachine(ports);assert m.init(0,0)==1 and m.get(hx['KdComPortInUse'])==expected
 assert m.ports[expected].dll==6
passed('Automatic selection prefers COM2 then COM1, with native 19200 default')

for com,base in [(1,0x3f8),(2,0x2f8),(3,0x3e8),(4,0x2e8)]:
 m=SerialMachine((base,));assert m.init(com,115200)==1 and m.get(hx['KdComPortInUse'])==base
 assert m.ports[base].dll==1
passed('Explicit COM1 through COM4 activate the requested detected UART')

m=SerialMachine((0x3f8,));assert m.init()==1;p=m.ports[0x3f8]
p.rx.extend([0x62,0xaa]);assert m.call('KdPortPollByte',BYTE)==0 and m.u.mem_read(BYTE,1)==b'b' and list(p.rx)==[0xaa]
assert m.call('KdPortGetByte',BYTE)==0 and m.u.mem_read(BYTE,1)==b'\xaa' and not p.rx
before=p.lsr_reads;assert m.call('KdPortPollByte',BYTE)==1 and p.lsr_reads-before<=3
passed('Poll consumes exactly one byte; get consumes next byte; empty polling is bounded')

for error in [2,4,8]:
 p.errors=error;p.rx.append(0x78);assert m.call('KdPortPollByte',BYTE)==2 and m.u.mem_read(BYTE,1)==b'\0';p.rx.clear()
p.errors=0;p.arrive_at=p.lsr_reads+4
assert m.call('KdPortGetByte',BYTE)==0 and m.u.mem_read(BYTE,1)==b'B'
passed('UART overrun/parity/framing errors report error; waiting receive handles delayed data')

before=p.lsr_reads;assert m.call('KdPortGetByte',BYTE,limit=20000000)==1
assert 204800<=p.lsr_reads-before<=204802
passed('Waiting receive returns no-data after the actual cportlib timeout loop')

p.tx_ready_at=p.lsr_reads+4;m.call('KdPortPutByte',0x5a);assert p.tx==[0x5a]
before=(p.dll,p.dlm,p.reg.copy());flags=sym['_HalpNt5DebugPort']+8
m.call('KdPortSave');assert m.get(flags)&4
m.call('KdPortRestore');assert not m.get(flags)&4 and before==(p.dll,p.dlm,p.reg)
passed('Transmit waits for readiness; save/restore toggles native debugger state without changing direct UART settings')

m.ports.clear();assert m.call('KdPortGetByte',BYTE)==1 and m.call('KdPortPollByte',BYTE)==1
m.call('KdPortPutByte',42);assert m.init()==0 and m.get(hx['KdComPortInUse'])==0
passed('Disconnected UART produces no-data and failed reinitialization releases the claimed port')

assert hashlib.sha256(kp.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
# Private native helper entries are pinned to that exact kernel and recorded
# in kd-contracts-disassembly.txt; these are not new exports in either binary.
hx['NativeReceiveBytes']=0x530ac2;hx['NativePollBreakIn']=0x429980
m=SerialMachine((0x3f8,));assert m.init()==1;p=m.ports[0x3f8]
p.rx.extend([0x12,0x34]);assert m.call('NativeReceiveBytes',BYTE,2)==0
assert m.u.mem_read(BYTE,2)==b'\x12\x34' and not p.rx
m.u.mem_write(kx['KdDebuggerEnabled'],b'\x01')
for byte,expected in [(0x61,0),(0x62,1)]:
 p.rx.append(byte);assert m.call('NativePollBreakIn')&255==expected and not p.rx
assert m.call('NativePollBreakIn')&255==0
passed('Installed kernel receive and break-in polling helpers consume bytes through the actual new HAL')

report={'scope':KD_SCOPE,'hal_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'kernel_sha256':hashlib.sha256(kp.read_bytes()).hexdigest(),'tests':results,
 'limitations':['IN/OUT model, not physical UART or xemu transport','Direct UART only; modem command protocol and ARC enumeration unsupported','No connected WinDbg session']}
(out/'kdport-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
