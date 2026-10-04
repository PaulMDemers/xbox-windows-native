"""Execute compiled VfatWrite with bounded caller MDLs and modeled disk/locks."""
import pathlib,sys,struct,json,hashlib,argparse
k=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ECX,UC_X86_REG_ESP,UC_X86_REG_EIP
parser=argparse.ArgumentParser();parser.add_argument('--eof',action='store_true');parser.add_argument('--completion',action='store_true');a=parser.parse_args();a.eof=a.eof or a.completion
path=k/('artifacts/xwnfatx-paging-completion.sys' if a.completion else 'artifacts/xwnfatx-paging-eof.sys' if a.eof else 'artifacts/xwnfatx-write-tail.sys');pe=pefile.PE(str(path));base=pe.OPTIONAL_HEADER.ImageBase
ns={};s=(k.parent/'native-windows-nt5-kernel/test-boundary.py').read_text();exec(s[s.index('def symbols(p):'):s.index('sym=symbols(h)')],{'struct':struct},ns);sym=ns['symbols'](pe)
C=0x800000;IRP=C+0x1000;FILE=C+0x2000;FCB=C+0x3000;DEV=C+0x4000;IOS=C+0x5000;GLOBAL=C+0x6000;MDL=C+0x7000;STOP=C+0x8000;SP=C+0xe000;TAIL=C+0x9000;TMDL=C+0xa000
def run(length,fail=None,paging=True,offset=0x20000,allocation=0x40000,canwait=True,file_size=0x40000):
 effective=min(length,max(0,file_size-offset)) if a.eof and paging else length
 u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(0,0x1000);u.mem_map(C,0x10000);u.mem_map(0xa00000,0x100000)
 buffer=0xb00000-length;payload=bytes((i*37+11)&255 for i in range(length));u.mem_write(buffer,payload)
 put=lambda at,v:u.mem_write(at,struct.pack('<I',v&0xffffffff));get=lambda at:struct.unpack('<I',u.mem_read(at,4))[0]
 disk=bytearray((i*13+3)&255 for i in range(0x50000));original=bytes(disk);calls=[];hooks={};state={'mutex':0,'resource':0,'pool':0,'mdl':0,'done':False}
 def args(n):return struct.unpack('<'+'I'*n,u.mem_read(u.reg_read(UC_X86_REG_ESP)+4,n*4))
 def ret(n,v=0):
  sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,v);u.reg_write(UC_X86_REG_ESP,sp+4+n*4);u.reg_write(UC_X86_REG_EIP,get(sp))
 def acquire():state['resource']+=1;calls.append('resource acquire');ret(2,1)
 def release():state['resource']-=1;ret(1)
 def mutex_acquire():
  calls.append('mutex acquire');assert state['resource']==1 and state['mutex']==0;state['mutex']=1;ret(0)
 def mutex_try():
  if fail=='mutex_busy':calls.append('mutex busy');ret(0,0)
  else:mutex_acquire();u.reg_write(UC_X86_REG_EAX,1)
 def mutex_release():assert state['mutex']==1;state['mutex']=0;ret(0)
 def lock():assert args(3)==(IRP,effective,0);ret(0,0)
 def allocate():
  assert args(3)[1]==512;calls.append('pool allocate')
  if fail=='pool':ret(3,0)
  else:state['pool']=1;ret(3,TAIL)
 def mdl_allocate():
  assert args(5)==(TAIL,512,0,0,0);calls.append('mdl allocate')
  if fail=='mdl':ret(5,0)
  else:state['mdl']=1;put(TMDL+12,TAIL);put(TMDL+20,512);ret(5,TMDL)
 def pool_free():assert state['pool'];state['pool']=0;ret(2)
 def mdl_free():assert state['mdl'];state['mdl']=0;ret(1)
 def io(write):
  ctx=u.reg_read(UC_X86_REG_EAX);n=u.reg_read(UC_X86_REG_EDX);lo,hi=args(2);assert ctx==C and hi==0 and n%512==0 and lo%512==0 and state['mutex']==1
  mdl=get(IRP+4);va=get(mdl+12);assert n<=get(mdl+20);calls.append(('write' if write else 'read',lo,n,'caller' if mdl==MDL else 'private'))
  error=(fail=='prefix' and write and mdl==MDL) or (fail=='read' and not write) or (fail=='tail' and write and mdl==TMDL)
  if not error:
   if write:disk[lo:lo+n]=u.mem_read(va,n)
   else:u.mem_write(va,bytes(disk[lo:lo+n]));put(args(3)[2],n-1 if fail=='short_read' else n)
  ret(0,0xc0000185 if error else 0)
 def copy():
  dst,src,n=args(3);u.mem_write(dst,bytes(u.mem_read(src,n)));ret(0,dst)
 def queue():calls.append('queued');ret(2)
 def stop():state['done']=True;u.emu_stop()
 hooks.update({STOP:stop,sym['_VfatLockUserBuffer']:lock,sym['_vfatDirEntryGetFirstCluster']:lambda:ret(0,2),sym['_VfatReadFileData']:lambda:io(False),sym['_VfatWriteFileData']:lambda:io(True)})
 handlers={'memmove':copy,'ExQueueWorkItem':queue,'ExAcquireResourceSharedLite':acquire,'ExAcquireResourceExclusiveLite':acquire,'ExReleaseResourceLite':release,'ExAcquireFastMutex':mutex_acquire,'ExTryToAcquireFastMutex':mutex_try,'ExReleaseFastMutex':mutex_release,'ExAllocatePoolWithTag':allocate,'IoAllocateMdl':mdl_allocate,'MmBuildMdlForNonPagedPool':lambda:ret(1),'IoFreeMdl':mdl_free,'ExFreePoolWithTag':pool_free}
 for lib in pe.DIRECTORY_ENTRY_IMPORT:
  for imp in lib.imports:
   name=imp.name.decode();target=STOP+0x100+len(hooks)*16;put(imp.address,target)
   def unexpected(n=name):raise AssertionError('Unexpected import '+n)
   hooks[target]=handlers.get(name,unexpected)
 put(sym['_VfatGlobalData'],GLOBAL);put(GLOBAL+4,0x900001);put(GLOBAL+12,1);put(DEV+0xf4,C+0xc000);put(C,IRP);put(C+4,0x900002);put(C+8,DEV);put(C+12,1 if canwait else 0);put(C+0x20,IOS);put(C+0x28,FILE)
 put(FILE+12,FCB);put(FCB+0xe4,FCB+0xf00);put(FCB+0x10,allocation);put(FCB+0x18,file_size);put(DEV+0xc0,512)
 put(IOS,4);put(IOS+4,length);put(IOS+12,offset);put(IRP+8,0x43 if paging else 1);put(IRP+0x60,IOS);put(IRP+4,MDL);u.mem_write(MDL+6,struct.pack('<H',1));put(MDL+12,buffer);put(MDL+20,length)
 u.hook_add(UC_HOOK_MEM_INVALID,lambda u,access,address,size,value,ctx:print('INVALID',hex(u.reg_read(UC_X86_REG_EIP)),hex(address),calls) or False)
 put(C+0xf000,C);put(SP,STOP);put(SP+4,C+0xf000);u.reg_write(UC_X86_REG_ESP,SP);u.hook_add(UC_HOOK_CODE,lambda u,pc,size,ctx:hooks[pc]() if pc in hooks else None);u.emu_start(sym['_VfatWrite'],0,count=200000)
 assert state=={'mutex':0,'resource':0,'pool':0,'mdl':0,'done':True},state
 status=u.reg_read(UC_X86_REG_EAX);assert get(IRP+4)==MDL
 invalid=offset%512 or ((not paging) and length%512) or (paging and effective and offset+((effective+511)&~511)>allocation)
 expected=0xc000000d if invalid else (0xc000009a if fail in ('pool','mdl') else (0xc0000185 if fail in ('prefix','read','tail') else (0xc00000e9 if fail=='short_read' else (0x103 if fail=='mutex_busy' else 0))))
 assert status==expected,(hex(status),hex(expected),calls)
 if status==0:
  assert disk[offset:offset+effective]==payload[:effective] and disk[:offset]==original[:offset] and disk[offset+effective:]==original[offset+effective:]
  assert get(IRP+28)==effective # IoStatus.Information
 elif not any(isinstance(v,tuple) and v[0]=='write' and v[3]=='caller' for v in calls):assert disk==original
 return {'length':length,'offset':offset,'paging':paging,'file_size':file_size,'effective_length':effective,'failure':fail,'status':hex(status),'calls':calls,'mdl_restored':True,'resources_released':True,'outside_bytes_preserved':status==0}
cases=[run(n) for n in (1,511,512,513,1016,65537)]
cases += [run(1016,fail=f) for f in ('pool','mdl','prefix','read','short_read','tail')]
cases += [run(1016,paging=False),run(1016,offset=1),run(1016,allocation=0x203f8),run(1016,fail='mutex_busy',canwait=False)]
if a.eof:cases += [run(65536,offset=0x180000,allocation=0,file_size=0),run(512,offset=0x20000,file_size=0x20000),run(4096,file_size=0x2036d),run(4096,file_size=0x20400),run(4096,file_size=0x20001)]
r={'scope':__doc__,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':cases,'passed':True,'limitation':'Models disk I/O and kernel locks; checks generated branch/order/cleanup, not actual scheduler contention.'}
(k/('paging-completion-tests.json' if a.completion else 'paging-eof-tests.json' if a.eof else 'write-tail-tests.json')).write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'compiled cases')
