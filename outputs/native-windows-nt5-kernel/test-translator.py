"""Run compiled NT5 translator callbacks with modeled kernel/PCI/PIC services.
No claim about physical interrupt delivery, resource arbitration, or PCI routing.
"""
import pathlib
SCOPE=__doc__
exec((pathlib.Path(__file__).resolve().parent/'test-boundary.py').read_text().split('m=Machine();m.frame();original=')[0])
P=STACK+0x1000;SRC=P+0x100;DST=P+0x200;ALT=P+0x300;COUNT=P+0x400;PTR=COUNT+4;POOL=P+0x1000
class Translation(Machine):
 def __init__(self,line=11,pin=1,allocation=True,property_status=0):
  super().__init__();self.line=line;self.pin=pin;self.allocation=allocation;self.property_status=property_status
  self.put(sym['_HalpEisaELCR'],0x1800)
  self.callbacks[hx['HalGetInterruptVector']]=self.vector
  self.callbacks[hx['HalGetBusDataByOffset']]=self.pci
  self.callbacks[kx['IoGetDeviceProperty']]=self.prop
  self.callbacks[kx['ExAllocatePoolWithTag']]=self.allocate
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.reg(UC_X86_REG_ESP)+4,n*4))
 def done(self,value,n):self.u.reg_write(UC_X86_REG_EAX,value);self.ret(n)
 def vector(self):
  bus,num,level,vector,irql,affinity=self.args(6)
  assert bus==1 and num==0 and level==vector and level<16
  self.u.mem_write(irql,bytes([27-level]));self.put(affinity,1)
  self.done(0 if level in [0,2,8] else 0x30+level,24)
 def pci(self):
  typ,bus,slot,buf,offset,length=self.args(6)
  assert typ==4 and bus==0 and slot==9 and offset==0x3c and length==2
  self.u.mem_write(buf,bytes([self.line,self.pin]));self.done(2,24)
 def prop(self):
  pdo,prop,length,buf,result=self.args(5)
  assert pdo==0x1234 and length==4
  # DEVICE_REGISTRY_PROPERTY: BusNumber 14, Address 16.
  assert prop in [14,16],prop
  self.put(buf,0 if prop==14 else 9<<16);self.put(result,4);self.done(self.property_status,20)
 def allocate(self):
  pool,size,tag=self.args(3);assert pool==1 and 32<=size<=16*32
  self.calls.append({'allocate_bytes':size});self.done(POOL if self.allocation else 0,12)
 def invoke(self,name,args):
  self.stopped=None;self.run(name,args=args)
  assert self.stopped=='return' and self.reg(UC_X86_REG_ESP)==STACK+0x7004+4*len(args)
  return self.reg(UC_X86_REG_EAX)
 def source(self,vector=11):self.u.mem_write(SRC,struct.pack('<BBHIII',2,3,0,vector,vector,0xffffffff))
 def requirement(self,low=1,high=15):
  self.u.mem_write(ALT,struct.pack('<BBBBHHIIIIII',1,2,3,0,0,0,low,high,0,0,0,0))

m=Translation();assert m.invoke('_HalpNt5GetInterruptTranslator@28',(0,0,5,24,0,P,P+40))==0
assert bytes(m.u.mem_read(P,4))==b'\x18\0\0\0' and m.get(P+4)==5
assert m.get(P+16)==sym['_HalpNt5TranslateResource@28'] and m.get(P+20)==sym['_HalpNt5TranslateRequirements@20']
passed('Actual Windows root PCI request installs the version-zero 24-byte translator and stdcall ABI')
for parent,bridge,size,version,ptr in [(0,5,23,0,P),(0,5,24,1,P),(0,5,24,0,0),(0,3,24,0,P),(7,5,24,0,P)]:
 m=Translation();m.u.mem_write(P,b'Z'*24)
 assert m.invoke('_HalpNt5GetInterruptTranslator@28',(parent,0,bridge,size,version,ptr,P+40))&0x80000000
 assert bytes(m.u.mem_read(P,24))==b'Z'*24
passed('Unsupported translator requests fail without publishing partial callbacks')
for line in [1,3,4,5,6,7,9,10,11,12,13,14,15]:
 m=Translation();m.source(line)
 assert m.invoke('_HalpNt5TranslateResource@28',(5,SRC,0,0,0,0x1234,DST))==0x120
 assert struct.unpack('<BBHIII',m.u.mem_read(DST,16))==(2,3,0 if line in [11,12] else 1,27-line,0x30+line,1)
passed('Child-to-parent supplies PIC vector/IRQL/affinity and uses the actual PIC trigger mode')
for line in [0,2,8,16,0xffffffff]:
 m=Translation();m.source(line);m.u.mem_write(DST,b'Z'*16)
 assert m.invoke('_HalpNt5TranslateResource@28',(5,SRC,0,0,0,0,DST))&0x80000000
 assert bytes(m.u.mem_read(DST,16))==b'Z'*16
passed('Invalid and HAL-reserved lines fail without changing the target')
m=Translation();m.source(0x3b)
assert m.invoke('_HalpNt5TranslateResource@28',(5,SRC,1,0,0,0x1234,DST))==0
assert struct.unpack('<III',m.u.mem_read(DST+4,12))==(11,11,0xffffffff)
passed('PCI reverse translation reads the device firmware line and matches the parent vector')
m=Translation();m.source(0x3e);m.requirement(13,0xffffffff)
assert m.invoke('_HalpNt5TranslateResource@28',(1,SRC,1,1,ALT,0,DST))==0
assert m.get(DST+8)==14
passed('Legacy reverse alternatives are bounded to 16 PIC lines even with ULONG_MAX upper bound')
m=Translation();m.requirement(0,0xffffffff)
assert m.invoke('_HalpNt5TranslateRequirements@20',(5,ALT,0x1234,COUNT,PTR))==0x120
assert m.get(COUNT)==1 and m.get(PTR)==POOL and m.get(POOL+8)==0x3b and m.get(POOL+12)==0x3b
assert bytes(m.u.mem_read(POOL,8))==bytes(m.u.mem_read(ALT,8))
passed('PCI requirements use firmware IRQ instead of unrestricted descriptor range and retain attributes')
for line,elcr in [(1,0),(6,0),(9,0),(9,1<<9),(11,0x1800)]:
 m=Translation(line=line);m.put(sym['_HalpEisaELCR'],elcr);m.requirement();m.u.mem_write(ALT+4,struct.pack('<H',0x8001))
 assert m.invoke('_HalpNt5TranslateRequirements@20',(5,ALT,0x1234,COUNT,PTR))==0x120
 assert struct.unpack('<H',m.u.mem_read(POOL+4,2))[0]==(0x8000 if elcr&(1<<line) else 0x8001)
 m.source(0x30+line);assert m.invoke('_HalpNt5TranslateResource@28',(5,SRC,1,0,0,0x1234,DST))==0
 assert struct.unpack('<H',m.u.mem_read(DST+2,2))[0]==(0 if elcr&(1<<line) else 1)
passed('USB/audio edge lines and ELCR level lines agree across forward, reverse and requirement translation; unrelated flag bits survive')
m=Translation();m.requirement(0,0xffffffff)
assert m.invoke('_HalpNt5TranslateRequirements@20',(1,ALT,0,COUNT,PTR))==0x120
assert m.get(COUNT)==13 and m.get(POOL+8)==0x31 and m.get(POOL+32+8)==0x33
assert m.u.mem_read(POOL+32,1)[0]==9
passed('Legacy requirements emit bounded valid alternatives, excluding reserved PIC lines')
for kwargs,ctx in [({'allocation':False},5),({'pin':0},5),({'line':255},5),({'property_status':0xc0000001},5)]:
 m=Translation(**kwargs);m.requirement();m.put(COUNT,0xdead);m.put(PTR,0xdead)
 assert m.invoke('_HalpNt5TranslateRequirements@20',(ctx,ALT,0x1234,COUNT,PTR))&0x80000000
 assert m.get(COUNT)==0 and m.get(PTR)==0
passed('Allocation, PCI property and unrouted interrupt failures leave empty requirement outputs')
(out/'translator-tests.json').write_text(json.dumps({'scope':SCOPE,'hal_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'results':results,'passed':True},indent=2)+'\n')
print(f'{len(results)} translator groups passed')

