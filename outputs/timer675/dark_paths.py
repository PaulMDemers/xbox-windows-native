"""Read pinned674 code into NEW isolated function fixtures; no boot/runtime reuse.
Show possible dark exits, not the actual physical674 cause.
"""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn674/build001')
out=K/'dark-paths001.json';assert not out.exists()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((K.parent/'watched674/build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert sha(B/'image-crom.bin')==old['artifacts']['image-crom.bin']['sha256']
sym={v[2]:int(v[0],16) for line in (B/'symbols.stdout').read_text().splitlines() if len(v:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r=dict(passed=False,physical_access=False,old_runtime_reused=False,source_sha256=sha(Path(__file__)),binary_sha256=sha(B/'image-crom.bin'),cases=[])
try:
 cases=[('entry-first-frozen',False,2,False,1,0),('entry-first-backward',False,2,True,1,0),
        ('entry-green-frozen',False,3,False,1,5),('entry-complete',False,0,False,0,0),
        ('report-first-frozen',True,2,False,1,0),('report-after-header-frozen',True,4,False,1,0),
        ('report-after-pulse-frozen',True,6,False,1,0),('report-complete',True,0,False,0,0x55)]
 for name,report,fail_at,backwards,expected_error,expected_mask in cases:
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob);uc.reg_write(x.UC_X86_REG_EFLAGS,2)
  state=dict(tx=0,reg=0,value=0,completed=[],mask=None,enabled=False,tick=0,reads=0,ports=0)
  def inp(uc,port,width,user):
   state['ports']+=1
   if port==0x8008:
    assert width==4;state['reads']+=1
    step=(-1 if backwards else 0) if fail_at and state['tx']>=fail_at else 5000
    state['tick']=(state['tick']+step)&0xffffffff;return state['tick']
   assert port==0xc000 and width in [1,2]
   if width==1:
    state['completed'].append([state['reg'],state['value']])
    if state['reg']==8:state['mask']=state['value']
    if state['reg']==7:assert state['value']==1;state['enabled']=True
   return 0x10
  def output(uc,port,width,value,user):
   state['ports']+=1
   if port==0xc008:assert width==1;state['reg']=value
   elif port==0xc006:assert width==2;state['value']=value
   elif port==0xc002:assert width==1 and value==0x1a;state['tx']+=1
   else:assert port==0xc004 and width==1 and value==0x20 or port==0xc000 and width==2
  def forbidden(*args):raise AssertionError('timer/indicator audit unexpectedly called network sender')
  uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,output,None,1,0,x.UC_X86_INS_OUT)
  uc.hook_add(u.UC_HOOK_CODE,forbidden,None,sym['NativeSend656'],sym['NativeSend656'])
  smc=0x027e0000;end=0x027ef000;sp=0x027fe000
  uc.mem_write(smc,pack(0,sym['signal_in'],sym['signal_out'],sym['signal_delay']))
  uc.mem_write(sym['Record670'],pack(2))
  record=sym['Final672' if report else 'Entry672']
  args=[smc,record,2,4] if report else []
  uc.mem_write(sp,pack(end,*args));uc.reg_write(x.UC_X86_REG_ESP,sp)
  uc.emu_start(sym['report672' if report else 'entry672'],end,timeout=30000000,count=50000000)
  assert uc.reg_read(x.UC_X86_REG_EIP)==end
  error=uc.reg_read(x.UC_X86_REG_EAX);words=struct.unpack('<9I',uc.mem_read(record,36))
  assert error==expected_error and state['enabled'] and state['mask']==expected_mask
  assert words[5]==(not expected_error)
  if expected_error:assert state['tx']==fail_at and words[1]==1
  r['cases'].append(dict(name=name,model='SMC immediate completion, clock failure injected at specified transaction count',error=error,emission=list(words),completed_smc=state['completed'],timer_reads=state['reads'],latched_mask_model=state['mask'],actual_hardware_cause_established=False))
  print(name,'PASS',flush=True)
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
