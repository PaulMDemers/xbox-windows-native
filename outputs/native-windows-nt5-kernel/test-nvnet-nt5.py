"""Execute NT5 miniport registration/glue instructions with modeled NDIS/kernel calls.
This does not model NIC DMA, networking, or a real kernel DPC scheduler.
"""
import pathlib,sys,json,hashlib,struct
out=pathlib.Path(__file__).resolve().parent;root=out.parents[1];sys.path.insert(0,str(root/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
code=(out/'test-boundary.py').read_text();ns={};exec(code[code.index('def symbols(p):'):code.index('sym=symbols(h)')],{'struct':struct},ns)
path=out/'artifacts/nvnetnt5.sys';pe=pefile.PE(str(path));sym=ns['symbols'](pe);base=pe.OPTIONAL_HEADER.ImageBase
STACK=0x800000;EXT=STACK+0x1000;STOP=0xa00000;TRAMP=STOP+0x100
results=[]
class Machine:
 def __init__(self,processors=1,wrapper=True,status=0):
  self.u=Uc(UC_ARCH_X86,UC_MODE_32);u=self.u;self.hooks={STOP:self.stop};self.calls=[];self.stopped=False;self.wrapper=wrapper;self.status=status
  for addr,size in [(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),(STACK,0x10000),(STOP,0x1000)]:u.mem_map(addr,size)
  u.mem_write(base,pe.get_memory_mapped_image());n=0
  for lib in pe.DIRECTORY_ENTRY_IMPORT:
   for imp in lib.imports:
    addr=TRAMP+n*16;n+=1;self.put(imp.address,addr);name=imp.name.decode()
    if name=='KeNumberProcessors':u.mem_write(addr,bytes([processors]))
    else:self.hooks[addr]=getattr(self,name,lambda name=name:(_ for _ in ()).throw(AssertionError('Unexpected service '+name)))
  u.hook_add(UC_HOOK_CODE,lambda u,a,size,ctx:self.hooks[a]() if a in self.hooks else None)
 def get(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
 def put(self,a,v):self.u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def stop(self):self.stopped=True;self.u.emu_stop()
 def args(self,n):return struct.unpack('<'+'I'*n,self.u.mem_read(self.u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(self,n,value=0):
  sp=self.u.reg_read(UC_X86_REG_ESP);ip=self.get(sp);self.u.reg_write(UC_X86_REG_EAX,value);self.u.reg_write(UC_X86_REG_ESP,sp+4+n*4);self.u.reg_write(UC_X86_REG_EIP,ip)
 def run(self,name,args=()):
  self.stopped=False;sp=STACK+0xf000
  for i,v in enumerate([STOP,*args]):self.put(sp+i*4,v)
  preserved={UC_X86_REG_EBX:0x11223344,UC_X86_REG_ESI:0x22334455,UC_X86_REG_EDI:0x33445566,UC_X86_REG_EBP:0x44556677}
  for register,value in preserved.items():self.u.reg_write(register,value)
  self.u.reg_write(UC_X86_REG_ESP,sp);self.u.emu_start(sym[name],0,count=50000)
  assert self.stopped and self.u.reg_read(UC_X86_REG_ESP)==sp+4+(len(args)*4 if '@' in name else 0)
  assert all(self.u.reg_read(k)==v for k,v in preserved.items())
  return self.u.reg_read(UC_X86_REG_EAX)
 def NdisInitializeWrapper(self):
  ptr,driver,path,unused=self.args(4);assert (driver,path,unused)==(0x1111,0x2222,0);self.put(ptr,0x1234 if self.wrapper else 0);self.calls.append('wrapper');self.ret(4)
 def NdisMRegisterMiniport(self):
  handle,ptr,size=self.args(3);assert handle==0x1234 and size==96
  self.characteristics=bytes(self.u.mem_read(ptr,size));self.calls.append('register');self.ret(3,self.status)
 def NdisTerminateWrapper(self):assert self.args(2)==(0x1234,0);self.calls.append('terminate');self.ret(2)
 def NdisMRegisterAdapterShutdownHandler(self):self.shutdown=self.args(3);self.calls.append('shutdown');self.ret(3)
 def KeInitializeEvent(self):
  self.event,type_,state=self.args(3);assert (type_,state)==(0,0);self.calls.append('event');self.ret(3)
 def KeInitializeDpc(self):
  self.dpc,self.callback,context=self.args(3);assert context==self.event;self.calls.append('dpc');self.ret(3)
 def KeSetImportanceDpc(self):assert self.args(2)==(self.dpc,0);self.calls.append('low');self.ret(2)
 def KeInsertQueueDpc(self):assert self.args(3)==(self.dpc,0,0);self.calls.append('queue');self.ret(3,1)
 def KeWaitForSingleObject(self):assert self.args(5)==(self.event,0,0,0,0);self.calls.append('wait');self.ret(5)
 def KeSetEvent(self):self.signal=self.args(3);self.calls.append('signal');self.ret(3)

m=Machine();assert m.run('_DriverEntry@8',(0x1111,0x2222))==0
assert m.characteristics[:2]==b'\x05\0'
for offset,name in [(20,'_MiniportHalt@4'),(24,'_MiniportHandleInterrupt@4'),(28,'_MiniportInitialize@24'),(32,'_MiniportISR@12'),(36,'_MiniportQueryInformation@24'),(64,'_NvNetNt5SendPackets@12'),(52,'_MiniportSetInformation@24')]:
 assert struct.unpack_from('<I',m.characteristics,offset)[0]==sym[name]
assert struct.unpack_from('<I',m.characteristics,48)[0]==0
results.append('NDIS 5.0 registration uses the native 96-byte callback layout and preserves stdcall state')
for cpus in [0,2,4]:
 m=Machine(processors=cpus);assert m.run('_DriverEntry@8',(0x1111,0x2222))==0xc00000bb and not m.calls
results.append('UP-only compatibility path rejects other processor counts before NDIS registration')
m=Machine(wrapper=False);assert m.run('_DriverEntry@8',(0x1111,0x2222))==0xc0000001 and m.calls==['wrapper']
m=Machine(status=0xc0010004);assert m.run('_DriverEntry@8',(0x1111,0x2222))==0xc0010004 and m.calls==['wrapper','register','terminate']
results.append('Wrapper and miniport-registration failures propagate and release wrapper ownership')
m=Machine();m.put(EXT+4,0x1234);m.run('_NvNetNt5RegisterShutdown',(EXT,))
assert m.shutdown==(0x1234,EXT,sym['_MiniportShutdown@4'])
results.append('Legacy shutdown registration passes the adapter context and real shutdown callback')
m=Machine();m.run('_NvNetNt5FlushDpcs');assert m.calls==['event','dpc','low','queue','wait']
assert m.callback==sym['_NvNetNt5DpcBarrier@16']
m.run('_NvNetNt5DpcBarrier@16',(m.dpc,m.event,0,0));assert m.signal==(m.event,0,0)
results.append('UP DPC barrier queues a low-importance entry before waiting and its callback signals the correct event')
# Exercise array ownership against modeled single-packet sends, including
# the first-resource-failure boundary where the tail must remain untouched.
for statuses in [[],[0x103],[0,0xc0000001,0x103],[0x103,0xc000009a,0x103],[0xc000009a,0]]:
 m=Machine();packets=[EXT+0x200+i*0x100 for i in range(len(statuses))];seen=[]
 for i,packet in enumerate(packets):
  m.put(EXT+i*4,packet)
  # Native NDIS_PACKET.Private.NdisPacketOobOffset is USHORT at byte 30.
  m.u.mem_write(packet+30,struct.pack('<H',64));m.put(packet+64+28,0xdeadbeef)
 def send():
  context,packet,flags=m.args(3);assert context==0x1234 and flags==0
  i=len(seen);assert packet==packets[i];seen.append(packet);m.ret(3,statuses[i])
 m.hooks[sym['_MiniportSend@12']]=send
 m.run('_NvNetNt5SendPackets@12',(0x1234,EXT,len(packets)))
 count=statuses.index(0xc000009a)+1 if 0xc000009a in statuses else len(statuses)
 assert len(seen)==count
 for i,packet in enumerate(packets):assert m.get(packet+64+28)==(statuses[i] if i<count else 0xdeadbeef)
results.append('Serialized array sends record each status and stop at resource exhaustion without touching the unaccepted tail')
layout=json.loads((out/'nvnet-layout.json').read_text())
afields=layout['NVNET_ADAPTER']['fields'];mfields=layout['MDL']['fields'];tfields=layout['NVNET_TCB']['fields']
for total,segments,expected in [(200,[100,100],0x103),(1514,[700,814],0x103),(0,[],0xc0010014),(1515,[1515],0xc0010014),(200,[201],0xc000009a),(200,[100,101],0xc000009a),(200,[100,99],0xc000009a)]:
 m=Machine();adapter=EXT;packet=EXT+0x800;mdl=EXT+0xa00;txbuf=EXT+0xc00;tcb=EXT+0xd00;dest=EXT+0x2000;transmit=TRAMP+0xd00;sent=[]
 m.put(adapter+afields['MaximumFrameSize'],1514);m.put(adapter+afields['Flags'],0x80000000)
 m.put(adapter+afields['Send.TcbSlots'],1);m.put(adapter+afields['Send.TbdSlots'],2)
 m.put(adapter+afields['Send.BufferList'],txbuf);m.put(adapter+afields['Send.CurrentTcb'],tcb);m.put(adapter+afields['TransmitPacket'],transmit)
 m.put(txbuf+4,dest);m.put(txbuf+8,0x00300000);m.u.mem_write(dest,b'\xcc'*1600)
 m.put(packet+4,total);m.put(packet+8,mdl if segments else 0);m.u.mem_write(packet+28,b'\x01')
 expected_data=b''
 for i,length in enumerate(segments):
  at=mdl+i*32;buf=EXT+0x4000+i*0x800;payload=bytes((i*77+j)&255 for j in range(length));expected_data+=payload
  m.put(at,mdl+(i+1)*32 if i+1<len(segments) else 0);m.u.mem_write(at+6,struct.pack('<H',1));m.put(at+12,buf);m.put(at+20,length);m.u.mem_write(buf,payload)
 def fastlock():m.ret(0)
 def move():
  d,src,size=m.args(3);m.u.mem_write(d,bytes(m.u.mem_read(src,size)));m.ret(0,d)
 def tx():
  context,control,sg=m.args(3);assert (context,control)==(adapter,tcb)
  assert m.get(sg)==1 and m.get(sg+8)==0x00300000 and m.get(sg+16)==total
  assert bytes(m.u.mem_read(dest,total))==expected_data, (total,segments,bytes(m.u.mem_read(dest,total)).hex(),expected_data.hex())
  m.put(tcb+tfields['Slots'],1);sent.append(True);m.ret(0)
 for lib in pe.DIRECTORY_ENTRY_IMPORT:
  for imp in lib.imports:
   if imp.name.decode() in ['KefAcquireSpinLockAtDpcLevel','KefReleaseSpinLockFromDpcLevel']:m.hooks[m.get(imp.address)]=fastlock
   if imp.name==b'memmove':m.hooks[m.get(imp.address)]=move
 m.hooks[transmit]=tx
 assert m.run('_MiniportSend@12',(adapter,packet,0))==expected,(total,segments)
 assert bool(sent)==(expected==0x103)
 assert bytes(m.u.mem_read(dest+1514,86))==b'\xcc'*86
 if expected==0xc000009a:
  assert m.get(adapter+afields['Send.BufferList'])==txbuf and m.get(adapter+afields['Send.TcbSlots'])==1
results.append('Contiguous transmit copies valid MDL chains, rejects zero/oversized frames and inconsistent lengths, and restores resources on copy failure')
report={'scope':__doc__,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tests':[{'test':s,'passed':True} for s in results]}
(out/'nvnet-nt5-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(len(results),'NDIS compatibility test groups passed')



