"""Execute the compiled HAL PCI loop, mocking only locked hardware transfers."""
import pathlib
kit=pathlib.Path(__file__).resolve().parent
base=kit.parent/'native-windows-nt5-kernel/test-boundary.py'
src=base.read_text().split('m=Machine();m.frame();original=')[0]
src=src.replace("hp=out/'artifacts/halxboxnt5.dll'", "hp=r/'outputs/native-windows-physical-f/artifacts/halxboxnt5-framebuffer.dll'")
exec(src)
out=kit
scope='Compiled HAL PCI loop; hardware transfers and synchronization mocked, no guest boot'
BH=STACK+0x100;BUF=STACK+0x1000;HANDLER=sym['_PCIConfigHandler']
class Pci(Machine):
 def __init__(self,change=None,bus=1,slot=0):
  super().__init__();self.bus=bus;self.slot=slot;self.lock=False;self.writes=[];self.reads=[]
  self.config=bytearray(range(256))
  for offset,value in [(0,0x02a010de),(12,0),(16,0xfd000000),(20,0xf0000008),(24,8)]:struct.pack_into('<I',self.config,offset,value)
  if change:struct.pack_into('<I',self.config,*change)
  self.put(BH+12,bus);self.put(BH+24,STACK+0x400)
  for index in range(8):
   addr=STOP+0x100+16*index;self.put(HANDLER+4*index,addr)
   self.callbacks[addr]=lambda n=index:self.io(n)
 def io(self,n):
  sp=self.reg(UC_X86_REG_ESP)
  if n==0:
   assert not self.lock;self.lock=True;self.ret(16);return
  if n==1:
   assert self.lock;self.lock=False;self.ret(8);return
  assert self.lock
  length=[4,1,2][(n-2)%3];buf=self.get(sp+12);off=self.get(sp+16)
  if n<5:
   self.reads.append((off,length));self.u.mem_write(buf,bytes(self.config[off:off+length]))
  else:
   self.writes.append((off,length));self.config[off:off+length]=self.u.mem_read(buf,length)
  self.u.reg_write(UC_X86_REG_EAX,length);self.ret(16)
 def access(self,offset,length,write=False):
  self.stopped=None;self.u.mem_write(BUF,bytes([0xa5])*256)
  self.run('_HalpPCIConfig@24',args=(BH,self.slot,BUF,offset,length,HANDLER+(20 if write else 8)))
  assert self.stopped=='return' and not self.lock and self.reg(UC_X86_REG_ESP)==STACK+0x701c
  return bytes(self.u.mem_read(BUF,length))

for offset in range(0,33):
 for length in range(0,65-offset):
  m=Pci();original=bytes(m.config);want=bytearray(original[offset:offset+length])
  for j in range(length):
   if 24<=offset+j<28:want[j]=0
  assert m.access(offset,length)==want
  m=Pci();want=bytearray(m.config)
  for j in range(length):
   if not 24<=offset+j<28:want[offset+j]=0xa5
  m.access(offset,length,True);assert m.config==want
  assert all(not (o<28 and o+n>24) for o,n in m.writes)
passed('All 1617 header intervals: partial/bulk reads zero BAR2 only; writes never reach BAR2 and preserve neighboring bytes')
for change in [(0,0x123410de),(12,0x10000),(16,0xfc000000),(20,0xe0000008),(24,0),(24,0xf8000008)]:
 m=Pci(change);assert m.access(0,64)==m.config[:64];m.access(24,4,True);assert m.config[24:28]==bytes([0xa5])*4
passed('Other device/header/layout, absent BAR2 and assigned BAR2 pass through')
for bus,slot in [(0,0),(1,1),(1,32),(2,0)]:
 m=Pci(bus=bus,slot=slot);assert m.access(0,64)==m.config[:64];m.access(24,4,True);assert m.config[24:28]==bytes([0xa5])*4
passed('Other buses, devices and functions pass through')
m=Pci();m.access(0,4);m.access(16,12,True);assert m.access(24,4)==bytes(4) and m.config[24:28]==b'\x08\0\0\0'
passed('Guard latches before sizing; changes to BAR0/BAR1 cannot expose or write BAR2')
m=Pci();m.access(24,0,True);assert not m.reads and not m.writes and m.get(sym['_HalpXboxFramebufferPciState'])==0
passed('Zero-length access does not sample, latch or write configuration')
(out/'framebuffer-pci-tests.json').write_text(json.dumps({'scope':scope,'hal_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'results':results,'passed':True},indent=2)+'\n')
print(f'{len(results)} groups passed')
