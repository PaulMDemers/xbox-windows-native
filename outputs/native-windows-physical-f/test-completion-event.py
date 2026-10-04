"""Execute compiled write-data batches with a previously signaled event and pending disk I/O."""
import pathlib,sys,struct,json,hashlib
k=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESP,UC_X86_REG_EIP
ns={};s=(k.parent/'native-windows-nt5-kernel/test-boundary.py').read_text();exec(s[s.index('def symbols(p):'):s.index('sym=symbols(h)')],{'struct':struct},ns)
def run(name,fat):
 path=k/'artifacts'/name;p=pefile.PE(str(path));base=p.OPTIONAL_HEADER.ImageBase;sy=ns['symbols'](p);u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,p.get_memory_mapped_image());C=0x800000;IRP=C+0x1000;FCB=C+0x2000;FILE=C+0x3000;DEV=C+0x4000;STOP=C+0x5000;SP=C+0xe000;u.mem_map(C,0x10000)
 put=lambda at,v:u.mem_write(at,struct.pack('<I',v&0xffffffff));get=lambda at:struct.unpack('<I',u.mem_read(at,4))[0]
 state={'signaled':True,'pending':False,'waits':0,'resets':0,'done':False}
 def args(n):return struct.unpack('<'+'I'*n,u.mem_read(u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(n,v=0):
  sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,v);u.reg_write(UC_X86_REG_ESP,sp+4+n*4);u.reg_write(UC_X86_REG_EIP,get(sp))
 def reset():assert args(3)==(C+0x30,0,0);state['signaled']=False;state['resets']+=1;ret(3)
 def write():
  assert args(5)[0]==C and args(5)[2:]==(512,0,0);state['pending']=True;put(C+0x2c,get(C+0x2c)+1);ret(0,0x103)
 def wait():
  assert args(5)[0]==C+0x30;state['waits']+=1
  if not state['signaled']:state['pending']=False;state['signaled']=True;put(C+0x2c,0)
  ret(5)
 def offset():put(args(5)[3],2);ret(0)
 def next_cluster():put(args(4)[2],0xffffffff);ret(0)
 def stop():state['done']=True;u.emu_stop()
 hooks={STOP:stop,sy['_VfatWriteDiskPartial']:write,sy['_vfatDirEntryGetFirstCluster']:lambda:ret(0,2),sy['_OffsetToCluster']:offset,sy['_NextCluster']:next_cluster}
 handlers={'KeInitializeEvent':reset,'KeWaitForSingleObject':wait,'ExAcquireFastMutex':lambda:ret(0),'ExReleaseFastMutex':lambda:ret(0)}
 for lib in p.DIRECTORY_ENTRY_IMPORT:
  for imp in lib.imports:
   target=STOP+0x100+len(hooks)*16;put(imp.address,target)
   def unexpected(n=imp.name):raise AssertionError(n)
   hooks[target]=handlers.get(imp.name.decode(),unexpected)
 put(C,IRP);put(C+8,DEV);put(C+0x28,FILE);put(FILE+12,FCB);put(FCB+0x148,4 if fat else 0);put(FCB+0x10,65536);put(FCB+0x18,65536);put(DEV+0xc0,512);put(DEV+0xc4,65536);put(DEV+0xa4,1)
 put(SP,STOP);put(SP+4,0);put(SP+8,0);u.reg_write(UC_X86_REG_ESP,SP);u.reg_write(UC_X86_REG_EAX,C);u.reg_write(UC_X86_REG_EDX,512);u.hook_add(UC_HOOK_CODE,lambda u,pc,size,ctx:hooks[pc]() if pc in hooks else None);u.emu_start(sy['_VfatWriteFileData'],0,count=200000)
 assert state['done'] and state['waits']==1
 fixed='completion' in name;assert state['pending']!=fixed and state['resets']==int(fixed),state
 return {'driver':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fat_branch':fat,**state,'premature_return':state['pending']}
r={'scope':__doc__,'cases':[run(n,f) for n in ('xwnfatx-paging-eof.sys','xwnfatx-paging-completion.sys') for f in (False,True)],'passed':True,'limitation':'Models lower disk submission and event wakeup; executes actual driver batching/refcount logic.'}
(k/'completion-event-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
