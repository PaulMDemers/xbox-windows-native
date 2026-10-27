"""Fresh execution of retained689 wrapper bytes before paging transition.
Kernel allocations are modeled; no kernel, device, native handoff or old runtime runs.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_EFLAGS
out=K/'legacy-audit002.json';assert not out.exists()
b=Path('C:/xwn689/build001/default.xbe').read_bytes()
assert hashlib.sha256(b).hexdigest()=='96016db66f620e7dd22210d67ded7a60936b593c2e8147c9b406d34c4bb96c0a'
obj='/home/paul/xbox-windows-native/xcal689-source001/boot_xbe/xbeboot.o'
sytext=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',obj],text=True)
sy={v[2]:int(v[0],16)+0x10000 for line in sytext.splitlines() if len(v:=line.split())==3 and v[1] in ['t','T']}
r={'passed':False,'scope':__doc__,'xbe_sha256':hashlib.sha256(b).hexdigest(),'symbols':sy,'symbol_source_sha256':hashlib.sha256(subprocess.check_output(['wsl','-d','Ubuntu','--','cat',obj])).hexdigest(),'cases':[]}
try:
 for case in ['exact_success','source_null','stub_null','virtual_failure','rounded_base']:
  u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(0,0x4000000);u.mem_map(0x80000000,0x2000000)
  u.mem_write(0x10000,b);u.reg_write(UC_X86_REG_ESP,0x2f08000);u.reg_write(UC_X86_REG_EFLAGS,0x202)
  for i,n in enumerate(['MmAllocateContiguousMemoryEx','MmGetPhysicalAddress','NtAllocateVirtualMemory']):u.mem_write(sy[n],struct.pack('<L',0x700000+i*0x10))
  state={'case':case,'calls':[],'allocation_count':0,'unowned_write':None,'null_physical_query':False,'transfer_reached':False}
  allowed=[(0x10000,0x10000+len(b)),(0x2f00000,0x2f10000)]
  def words(a,n):return struct.unpack('<'+'L'*n,u.mem_read(a,4*n))
  def ret(value,n):
   sp=u.reg_read(UC_X86_REG_ESP);dest=words(sp,1)[0];u.reg_write(UC_X86_REG_ESP,sp+4+4*n);u.reg_write(UC_X86_REG_EAX,value);u.reg_write(UC_X86_REG_EIP,dest)
  def code(uc,pc,size,_):
   if pc in (0x1fff000,0x1ff0000):state['transfer_reached']=True;u.emu_stop();return
   if pc not in (0x700000,0x700010,0x700020):return
   sp=u.reg_read(UC_X86_REG_ESP)
   if pc==0x700000:
    args=words(sp+4,5);state['allocation_count']+=1;i=state['allocation_count']
    v=0x80200000 if i==1 else 0x81fff000
    if (i==1 and case=='source_null') or (i==2 and case=='stub_null'):v=0
    if v:allowed.append((v,v+args[0]))
    state['calls'].append({'api':'MmAllocateContiguousMemoryEx','args':list(args),'result':v});ret(v,5)
   elif pc==0x700010:
    a=words(sp+4,1)[0];state['calls'].append({'api':'MmGetPhysicalAddress','argument':a})
    if a==0:state['null_physical_query']=True;u.emu_stop();return
    ret(a&0x7fffffff,1)
   else:
    args=words(sp+4,5);requested=words(args[0],1)[0];n=words(args[2],1)[0]
    v=requested if case!='rounded_base' else requested&~0xffff
    n=n if case!='rounded_base' else 0x10000
    status=0xc0000018 if case=='virtual_failure' else 0
    if not status:
     u.mem_write(args[0],struct.pack('<L',v));u.mem_write(args[2],struct.pack('<L',n));allowed.append((v,v+n))
    state['calls'].append({'api':'NtAllocateVirtualMemory','requested':requested,'returned':v,'size':n,'status':status});ret(status,5)
  def write(uc,access,a,n,v,_):
   if not any(lo<=a and a+n<=hi for lo,hi in allowed):state['unowned_write']={'address':a,'bytes':n};u.emu_stop()
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start(sy['_start'],0x3ffff00,count=2000000)
  if case=='exact_success':assert state['transfer_reached'] and not state['unowned_write']
  elif case in ('source_null','stub_null'):assert state['null_physical_query']
  else:assert state['unowned_write'] and not state['transfer_reached']
  state['expected_observed']=True;r['cases'].append(state)
 r['stub_copy_bytes']=1024;r['required_stub_bytes_through_gdt_descriptor']=sy['gdt_48_base']+4-sy['blentry']
 assert r['required_stub_bytes_through_gdt_descriptor']<=1024
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS five pre-transfer wrapper models; unchecked failures confirmed only in modeled cases')
