"""Execute built x86 routines with mocked kernel services in Unicorn.

This tests calling conventions, argument forwarding and mutex state changes.
It is NOT a Windows boot, scheduler test, or interrupt/hardware validation.
"""
import hashlib,json,pathlib,struct,sys
r=pathlib.Path(__file__).resolve().parents[2];out=r/'outputs/native-windows-nt5'
sys.path.insert(0,str(r/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
path=out/'artifacts/halxboxnt5.dll';pe=pefile.PE(str(path));base=pe.OPTIONAL_HEADER.ImageBase
exports={s.name.decode():base+s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
STACK=0x800000;DATA=0x900000;TRAMPS=0xa00000;STOP=TRAMPS+0xf000;THREAD=0xdeadbeec
class Machine:
    def __init__(self):
        self.u=Uc(UC_ARCH_X86,UC_MODE_32);u=self.u
        u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
        u.mem_write(base,pe.get_memory_mapped_image())
        for addr in (STACK,DATA,TRAMPS):u.mem_map(addr,0x10000)
        u.mem_map(0xffdff000,4096);self.put(0xffdff124,THREAD)
        self.callbacks={};self.irql=0;self.waits=[];self.signals=[];self.calls=[]
        k=0
        for d in pe.DIRECTORY_ENTRY_IMPORT:
            for sym in d.imports:
                name=sym.name.decode();addr=TRAMPS+k*16;k+=1
                self.put(sym.address,DATA+0x2000 if name=='HalDispatchTable' else addr)
                self.callbacks[addr]=name
        self.callbacks[exports['KfRaiseIrql']]='raise';self.callbacks[exports['KfLowerIrql']]='lower'
        for offset,count in ((0x18,4),(0x1c,4),(0x20,4),(0x24,5)):
            addr=TRAMPS+0xe000+offset
            self.put(DATA+0x2000+offset,addr);self.callbacks[addr]=('dispatch',count)
        u.hook_add(UC_HOOK_CODE,self.hook)
    def get(self,addr):return struct.unpack('<I',self.u.mem_read(addr,4))[0]
    def put(self,addr,v):self.u.mem_write(addr,struct.pack('<I',v&0xffffffff))
    def ret(self,value=0,pop=0):
        u=self.u;sp=u.reg_read(UC_X86_REG_ESP);ip=self.get(sp)
        u.reg_write(UC_X86_REG_EAX,value&0xffffffff);u.reg_write(UC_X86_REG_ESP,sp+4+pop);u.reg_write(UC_X86_REG_EIP,ip)
    def hook(self,u,addr,size,ctx):
        if addr==STOP:u.emu_stop();return
        kind=self.callbacks.get(addr)
        if kind is None:return
        sp=u.reg_read(UC_X86_REG_ESP);cx=u.reg_read(UC_X86_REG_ECX)
        if kind=='raise':old=self.irql;self.irql=cx&255;self.ret(old)
        elif kind=='lower':self.irql=cx&255;self.ret()
        elif kind=='KeWaitForSingleObject':
            args=[self.get(sp+4+i*4) for i in range(5)];self.waits.append(args)
            assert self.irql==1 and args[0]==DATA+12 and args[1:]==[0,0,0,0]
            # Simulate the current owner releasing once before wakeup.
            self.put(DATA,self.get(DATA)+1);self.ret(0,20)
        elif kind=='KeSetEventBoostPriority':
            args=[self.get(sp+4+i*4) for i in range(2)];self.signals.append(args)
            assert self.irql==1 and args==[DATA+12,0];self.ret(0,8)
        elif isinstance(kind,tuple):
            count=kind[1];args=[cx,u.reg_read(UC_X86_REG_EDX)]+[self.get(sp+4+i*4) for i in range(count-2)]
            self.calls.append(args);self.ret(0x12345678,(count-2)*4)
        else:raise AssertionError('Unexpected kernel call '+kind)
    def call(self,name,args,fastcall=False):
        u=self.u;stackargs=args[2:] if fastcall else args
        sp=STACK+0x8000
        for i,value in enumerate([STOP]+stackargs):self.put(sp+i*4,value)
        u.reg_write(UC_X86_REG_ESP,sp)
        if fastcall:
            u.reg_write(UC_X86_REG_ECX,args[0]);u.reg_write(UC_X86_REG_EDX,args[1] if len(args)>1 else 0)
        preserved={UC_X86_REG_EBX:0x1111,UC_X86_REG_ESI:0x2222,UC_X86_REG_EDI:0x3333,UC_X86_REG_EBP:0x4444}
        for reg,val in preserved.items():u.reg_write(reg,val)
        u.emu_start(exports[name],STOP+1,count=10000)
        assert u.reg_read(UC_X86_REG_EIP)==STOP,'Routine did not return'
        assert u.reg_read(UC_X86_REG_ESP)==sp+4+len(stackargs)*4,'Stack cleanup mismatch'
        assert all(u.reg_read(reg)==val for reg,val in preserved.items()),'Nonvolatile register clobber'
        return u.reg_read(UC_X86_REG_EAX)

results=[]
def passed(name):results.append({'test':name,'passed':True})
m=Machine();m.put(DATA,1);m.call('ExAcquireFastMutex',[DATA],True)
assert (m.get(DATA),m.get(DATA+4),m.get(DATA+28),m.irql)==(0,THREAD,0,1)
assert not m.waits
m.call('ExReleaseFastMutex',[DATA],True)
assert (m.get(DATA),m.get(DATA+4),m.irql)==(1,0,0) and not m.signals
passed('Uncontended acquire/release, owner, IRQL, stack and preserved registers')
m=Machine();m.put(DATA,1);m.irql=1
assert m.call('ExTryToAcquireFastMutex',[DATA],True)==1
assert (m.get(DATA),m.get(DATA+4),m.get(DATA+28),m.irql)==(0,THREAD,1,1)
m.call('ExReleaseFastMutex',[DATA],True);assert m.irql==1
passed('Try-acquire succeeds and preserves caller APC level through release')
m=Machine();m.put(DATA,0);m.put(DATA+4,0x77777777)
assert m.call('ExTryToAcquireFastMutex',[DATA],True)==0
assert (m.get(DATA),m.get(DATA+4),m.irql)==(0,0x77777777,0)
passed('Failed try leaves ownership/count intact and restores caller IRQL')
m=Machine();m.put(DATA,0);m.call('ExAcquireFastMutex',[DATA],True)
assert len(m.waits)==1 and (m.get(DATA),m.get(DATA+8),m.get(DATA+4))==(0,1,THREAD)
passed('Contended acquire records contention and waits on correct event')
m=Machine();m.put(DATA,-1);m.put(DATA+4,THREAD);m.irql=1
m.call('ExReleaseFastMutex',[DATA],True)
assert m.get(DATA)==0 and len(m.signals)==1 and m.irql==0
passed('Release wakes a waiter with priority boost before lowering IRQL')
for name,count in [('IoAssignDriveLetters',4),('IoReadPartitionTable',4),('IoSetPartitionInformation',4),('IoWritePartitionTable',5)]:
    m=Machine();args=[0x100+i for i in range(count)]
    # The recognized-partitions parameter is BOOLEAN and must fit one byte.
    if name=='IoReadPartitionTable':args[2]=1
    ret=m.call(name,args)
    assert m.calls==[args]
    if name!='IoAssignDriveLetters':assert ret==0x12345678
    passed(name+' stdcall export forwards to fastcall dispatch with correct stack cleanup')
for name in ['KeTryToAcquireQueuedSpinLock','KeTryToAcquireQueuedSpinLockRaiseToSynch']:
    m=Machine();assert m.call(name,[0,DATA],True)==1
    assert m.irql==2 and m.get(DATA)==0
    passed(name+' free UP exclusion uses raised IRQL without a kernel helper')
report={'hal_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Actual built x86 instructions; mocked kernel services and serialized wait. No scheduler, interrupts or Windows runtime tested.','tests':results}
(out/'binary-unit-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
