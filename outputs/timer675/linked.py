"""Fresh isolated675 machine-code fixtures. I/O/clock are explicit models."""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn675/host001')
out=K/'linked001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=json.loads((K/'host001.json').read_text());assert host['passed']
blob=(B/'probe.bin').read_bytes();assert sha(B/'probe.bin')==host['artifacts']['probe.bin']['sha256']
sym={v[2]:int(v[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(v:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r=dict(passed=False,physical_access=False,new_XBE=False,source_sha256=sha(Path(__file__)),binary_sha256=sha(B/'probe.bin'),cases=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cases=['advance','slow','frozen','backward','jump','wrap32','hypothetical-wrap24','if-entry','if-after-entry','if-after-timer']
 cases += [f'smc-{transaction}-{mode}' for transaction in [1,2,3] for mode in ['busy','pending','error']]
 for case in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x100000);uc.mem_write(0x100000,blob)
  uc.reg_write(x.UC_X86_REG_EFLAGS,0x202 if case=='if-entry' else 2)
  failtx,mode=(int(case.split('-')[1]),case.split('-')[2]) if case.startswith('smc-') else (0,'none')
  tick=0xffffff00 if case=='wrap32' else 0x00ffff00 if case=='hypothetical-wrap24' else 100000 if case=='backward' else 0
  step=0 if case=='frozen' else -1 if case=='backward' else 3579546 if case=='jump' else 1 if case=='slow' else 100
  mask=0x00ffffff if case=='hypothetical-wrap24' else 0xffffffff
  state=dict(reads=0,ports=0,tx=0,pending_reg=0,pending_value=0,commands=[],flags_calls=0,held=False,first=[],last=0)
  def inp(uc,port,width,user):
   nonlocal_dummy=None
   global tick
   state['ports']+=1
   if port==0x8008:
    assert width==4;tick=(tick+step)&mask;state['reads']+=1;state['last']=tick
    if len(state['first'])<64:state['first'].append(tick)
    return tick
   assert port==0xc000 and width in [1,2]
   if width==2 and state['tx']+1==failtx and mode=='busy':return 0x800
   if width==1 and state['tx']==failtx:return 0 if mode=='pending' else 0x26 if mode=='error' else 0x10
   return 0x10
  def output(uc,port,width,value,user):
   state['ports']+=1
   if port==0xc008:assert width==1;state['pending_reg']=value
   elif port==0xc006:assert width==2;state['pending_value']=value
   elif port==0xc002:
    assert width==1 and value==0x1a;state['tx']+=1;state['commands'].append([state['pending_reg'],state['pending_value']])
   else:assert port==0xc004 and width==1 and value==0x20 or port==0xc000 and width==2
  def flags(uc,a,size,user):
   state['flags_calls']+=1
   if (case=='if-after-entry' and state['flags_calls']==2) or (case=='if-after-timer' and state['flags_calls']==3):
    uc.reg_write(x.UC_X86_REG_EFLAGS,uc.reg_read(x.UC_X86_REG_EFLAGS)|512)
  def forbidden(*args):raise AssertionError('unexpected NIC/frame call')
  def hold(uc,a,size,user):
   assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512;state['held']=True;uc.emu_stop()
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,flags,None,sym['flags'],sym['flags'])
  for name in ['send656','frame656']:uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym[name],sym[name])
  uc.hook_add(u.UC_HOOK_CODE,hold,None,sym['irq_hold669']+1,sym['irq_hold669']+1)
  def call():
   uc.reg_write(x.UC_X86_REG_ESP,0x1fe000);uc.mem_write(0x1fe000,pack(0x1ff000))
   uc.emu_start(sym['terminal675'],0x1ff000,timeout=30000000,count=50000000);assert state['held']
  call();raw=bytes(uc.mem_read(sym['Record675'],404));v=struct.unpack('<101I',raw)
  assert v[10]==state['reads'] and v[11]==len(state['first']) and list(v[12:12+v[11]])==state['first'] and v[76]==state['last']
  assert v[85+9]==state['reads'] and v[85]==0
  assert all(command!=[8,0] for command in state['commands'])
  if case.startswith('if-'):
   assert v[1]==3 and not v[4] and state['tx']==(0 if case=='if-entry' else 2)
   assert state['reads']==(37 if case=='if-after-timer' else 0)
  elif failtx:
   assert v[1]==(5 if failtx==3 else 4) and not v[4]
   assert v[79]==(0 if mode=='error' else 1) and state['tx']==(failtx-1 if mode=='busy' else failtx)
   assert state['reads']==(37 if failtx==3 else 0)
  else:
   err=4 if case in ['frozen','backward','jump','hypothetical-wrap24'] else 0
   assert v[0]==5 and v[1]==0 and v[4]==1 and v[9]==err and not v[79]
   assert state['commands']==[[8,0x5f],[7,1],[8,0xa5 if err else 0x0f]]
   expected={'advance':37,'slow':3581,'frozen':200001,'backward':2,'jump':2,'wrap32':37,'hypothetical-wrap24':3}[case]
   assert state['reads']==expected
  # Fresh function fixture only: repeat to prove one-shot hold, never a boot rerun.
  old=(state['ports'],state['reads']);state['held']=False;call()
  assert bytes(uc.mem_read(sym['Record675'],404))==raw and old==(state['ports'],state['reads'])
  r['cases'].append(dict(name=case,phase=v[0],error=v[1],timer_error=v[9],timer_samples=v[10],raw_prefix=list(v[12:12+v[11]]),last_sample=v[76],entry_error=v[77],final_error=v[78],refused_waits=v[79],commands=state['commands'],held=True,repeat_no_io=True));save()
  print(case,'PASS',flush=True)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);r['failed_case']=case;raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
