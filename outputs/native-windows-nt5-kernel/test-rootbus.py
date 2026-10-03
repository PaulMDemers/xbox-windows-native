"""Execute compiled root-aperture builders, mocking allocation and HAL claims."""
import pathlib
SCOPE=__doc__
exec((pathlib.Path(__file__).resolve().parent/'test-boundary.py').read_text().split('m=Machine();m.frame();original=')[0])
OUT=STACK+0x100;CLAIMS=STACK+0x1000;ALLOC=STACK+0x2000
class Root(Machine):
 def __init__(self,claims=(),fail=0):
  super().__init__();self.allocations=[];self.freed=[];self.fail=fail
  self.callbacks[kx['ExAllocatePoolWithTag']]=self.allocate
  self.callbacks[kx['ExFreePool']]=self.free
  self.put(sym['_HalpAddressUsageList'],CLAIMS)
  self.u.mem_write(CLAIMS,struct.pack('<IIBxxx',0,1,1)+b''.join(struct.pack('<II',a,n) for a,n in claims)+bytes(8))
 def allocate(self):
  sp=self.reg(UC_X86_REG_ESP);pool=self.get(sp+4);size=self.get(sp+8)
  assert pool==1 and size<4096
  pointer=0 if len(self.allocations)+1==self.fail else ALLOC+len(self.allocations)*4096
  self.allocations.append((pointer,size));self.u.reg_write(UC_X86_REG_EAX,pointer);self.ret(12)
 def free(self):
  self.freed.append(self.get(self.reg(UC_X86_REG_ESP)+4));self.ret(4)
 def invoke(self,requirements=False):
  self.put(OUT,0xdead)
  self.run('_HalpNt5QueryRootRequirements@4' if requirements else '_HalpNt5QueryRootResources@4',args=(OUT,))
  assert self.stopped=='return' and self.reg(UC_X86_REG_ESP)==STACK+0x7008
  return self.reg(UC_X86_REG_EAX)
 def descriptors(self):
  p=self.get(OUT);count=self.get(p+16)
  assert self.get(p)==1 and self.get(p+4)==15 and self.get(p+8)==0xffffffff
  return [struct.unpack('<BBHQI',self.u.mem_read(p+20+16*i,16)) for i in range(count)]

m=Root();assert m.invoke()==0;desc=m.descriptors()
assert len(desc)==3 and desc[0][:3]==(6,3,0)
assert desc[1]==(1,3,1,0,65536)
assert desc[2]==(3,3,0,0xf0000000,0x0f000000)
passed('Native PNPBus root list exposes bus numbers, 16-bit ports and bounded Xbox high MMIO')
claims=[(0xa0,2),(0x20,2),(0,32),(0x18,16),(0xcf8,8),(0xfff0,0xffffffff)]
m=Root(claims);assert m.invoke()==0;ports=[(d[3],d[3]+d[4]) for d in m.descriptors() if d[0]==1]
assert ports==[(0x28,0xa0),(0xa2,0xcf8),(0xd00,0xfff0)]
passed('Unsorted, overlapping and oversized reservations are merged and clipped without advertising HAL ports')
m=Root([(0,65536)]);assert m.invoke()==0;assert len(m.descriptors())==2
passed('Completely reserved port space yields no port window')
m=Root(claims);assert m.invoke(True)==0
p=m.get(OUT);size=m.get(p);count=m.get(p+36)
assert m.get(p+4)==15 and m.get(p+8)==0xffffffff and m.get(p+28)==1
assert size==40+count*32 and count==6 and m.freed==[ALLOC]
rows=[struct.unpack('<BBBBHH6I',m.u.mem_read(p+40+i*32,32)) for i in range(count)]
assert rows[0][:6]==(1,128,3,0,0,0) and rows[0][6]==1
assert rows[1][1]==6 and rows[1][6:9]==(256,0,255)
for row,(lo,hi) in zip(rows[2:-1],ports):
 assert row[:6]==(1,1,3,0,1,0)
 assert row[6:]==(hi-lo,1,lo,0,hi-1,0)
assert rows[-1][6:]==(0x0f000000,1,0xf0000000,0,0xfeffffff,0)
passed('Fixed resource requirements match every returned window, with native config-priority and bus-number descriptors')
for fail in [1,2]:
 m=Root(fail=fail);assert m.invoke(True)==0xc000009a and m.get(OUT)==0
 assert m.freed==([] if fail==1 else [ALLOC])
passed('Both allocation failures leave null output and free temporary resources')
m=Root([(i*4,1) for i in range(65)]);assert m.invoke()==0xc000009a and m.get(OUT)==0 and not m.allocations
passed('Reservation count guard fails closed without overflowing stack arrays')
(out/'rootbus-tests.json').write_text(json.dumps({'scope':SCOPE,'hal_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'results':results,'passed':True},indent=2)+'\n')
print(f'{len(results)} root bus groups passed')
