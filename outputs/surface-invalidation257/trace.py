"""ONE independent immutable GPU snapshot at a selected CPU-stopped loader phase."""
import datetime,ftplib,hashlib,json,os,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','preserve001']
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase257-runs/nt5-phase257-'+case)
assert (run/'instance.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
sys.path.insert(0,str(ws/'work/python-packages'));import capstone
from parsing import span,snapshot_tuple
from preservation import preconditions,preserve_tuple
from schema import parse as inventory_tuple,qualify as inventory_qualify
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
phase={'control001':'xbe','preserve001':'xbe'}[case]
r=dict(case=case,phase=phase,scope=__doc__,debugger=True,physical_access=False,gpu_ownership_qualified=False,ordinary_qualified=False,debugger_memory_writes=False,debugger_register_writes=False,passed=False,dirty_surface_coverage=False,host_vram_preservation=case=='preserve001',reference_observation=True,started_utc=utc(),monitor=[],events=[],gdb_requests=[])
g=None;lock=None;stopped=False;armed=[];quarantined=False
frontend_requested=False;frontend_reopened=False
worker_requested=False;worker_released=False
def save():
 p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def cmd(s):
 value=command(4594,s);r['monitor'].append(dict(utc=utc(),command=s,reply=value));save();return value
def ask(s):
 value=g.ask(s);r['gdb_requests'].append(dict(command=s,reply=value));save();return value
def regs():
 raw=bytes.fromhex(ask('g'));assert len(raw)>=40;return list(struct.unpack('<10I',raw[:40]))
def qom_path(tree):
 stack=[];found=[]
 for line in tree.splitlines():
  m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
  if not m:continue
  level=len(m[1]);name=m[2]
  while stack and stack[-1][0]>=level:stack.pop()
  if name:stack.append((level,name))
  if m[3]=='nv2a':found.append('/'+'/'.join(v for _,v in stack))
 assert len(found)==1;return found[0]
def wait_dashboard(deadline):
 attempts=0
 while True:
  attempts+=1
  try:
   with DeadlineFTP(min(deadline,time.monotonic()+6)) as ftp:
    ftp.connect('127.0.0.1',4596,timeout=ftp.budget());ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
    return dict(utc=utc(),reply=ftp.sendcmd('NOOP'),attempts=attempts,physical_access=False)
  except ftplib.all_errors:
   if time.monotonic()>=deadline:raise
   time.sleep(min(.2,max(0,deadline-time.monotonic())))
def restore_physical_mode(remote,record):
 if not record.get('physical_mode_restore_required'):return True
 try:
  ok=remote.ask('Qqemu.PhyMemMode:0')=='OK' and remote.ask('qqemu.PhyMemMode')=='0';record['physical_mode_restored']=ok
  if ok:record['physical_read_mode']=False;record['physical_mode_restore_required']=False
  return ok
 except Exception as exc:record['physical_mode_restore_error']=repr(exc);record['physical_mode_restored']=False;return False
def arm(kind,address,n):
 item=(kind,address,n);armed.append(item);r['armed_debugger_points']=armed.copy();save()
 assert ask(f'Z{kind},{address:x},{n:x}')=='OK'
def remove(item):
 kind,address,n=item;assert ask(f'z{kind},{address:x},{n:x}')=='OK';armed.remove(item);r['armed_debugger_points']=armed.copy();save()
def continue_stop(seconds):
 global stopped
 assert stopped and time.monotonic()+seconds<=overall+1
 g.s.settimeout(seconds);g.send('c');stopped=False
 try:reply=g.recv();stopped=True;return reply
 except socket.timeout:
  g.s.settimeout(5);reply=g.interrupt();stopped=True;raise AssertionError('Bounded guest stop not reached: '+reply)
 finally:g.s.settimeout(5)
def resident(name,address,n):
 data=g.read(address,n);p=out/'artifacts'/(name+'.bin');p.write_bytes(data)
 return data,dict(address=address,bytes=n,sha256=sha(p),path=p.relative_to(ws).as_posix())
def take_snapshot(name,values):
 assert stopped and 'phase_snapshot' not in r
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 initial=cmd('qom-get '+path+' xwn-snapshot238-report')
 assert re.search(r'(?<![a-z_])state=0(?:[, ]|$)',initial),initial
 row=dict(phase=phase,cpu_phase=name,registers=values,requested_utc=utc(),initial_reply=initial,request_may_be_accepted=True)
 r['phase_snapshot']=row;save()
 response=cmd('qom-set '+path+' xwn-snapshot238 true');row['set_reply']=response;save();assert 'Error' not in response,response
 deadline=time.monotonic()+8
 while True:
  report=cmd('qom-get '+path+' xwn-snapshot238-report');m=re.search(r'(?<![a-z_])state=(\d+)',report);assert m,report;state=int(m[1])
  if state in [3,5]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 row.update(terminal_state=state,terminal_reply=report,observed_utc=utc());save()
 assert state==3,'Bounded worker snapshot timed out; terminal evidence preserved'
 row['tuple']=snapshot_tuple(report);save()
 repeat=cmd('qom-get '+path+' xwn-snapshot238-report');row['immutable_reread_reply']=repeat;row['immutable_reread_matched']=repeat==report;save();assert repeat==report
 row['passed']=True;save()

def preservation_experiment():
 global quarantined
 t=r['phase_snapshot']['tuple'];ranges=preconditions(t)
 row=dict(kind=case,preconditions_passed=True,ranges=ranges,request_accepted=False,ownership_qualified=False,references_retired=False,started_utc=utc(),ram=[])
 r['preservation']=row;save()
 def capture(label):
  values=[]
  for i,s in enumerate(ranges):
   p=out/'artifacts'/f'{label}-range{i}.bin';assert not p.exists()
   reply=cmd(f'pmemsave {s[0]:#x} {s[1]} '+json.dumps(p.resolve().as_posix()))
   assert 'Error' not in reply and p.exists() and p.stat().st_size==s[1]
   data=p.read_bytes();values.append(dict(address=s[0],bytes=s[1],sha256=sha(p),path=p.relative_to(ws).as_posix()))
  row['ram'].append(dict(label=label,ranges=values));save()
 path=r['nv2a_qom_path'];initial=cmd('qom-get '+path+' xwn-preserve227-report')
 assert re.search(r'(?<![a-z_])state=0(?:[, ]|$)',initial)
 row['initial_reply']=initial;save()
 if case=='preserve001':
  row['request_may_be_accepted']=True;save()
  reply=cmd('qom-set '+path+' xwn-preserve227 true');row['set_reply']=reply;save()
  assert 'Error' not in reply,'No retry after setter failure'
  row['request_accepted']=True;save();deadline=time.monotonic()+8
  while True:
   report=cmd('qom-get '+path+' xwn-preserve227-report');state=int(re.search(r'(?<![a-z_])state=(\d+)',report)[1])
   if state in [3,4,5,6]:break
   assert time.monotonic()<deadline;time.sleep(.025)
  row.update(terminal_state=state,terminal_reply=report,observed_utc=utc());save()
  row['result']=preserve_tuple(report);r['preserve_result']=row['result'];save()
  repeat=cmd('qom-get '+path+' xwn-preserve227-report');row['immutable_reread_matched']=repeat==report;save();assert repeat==report
  if state in [5,6]:quarantined=True
  assert state==3,'Preservation failed/refused; evidence retained, never retry'
  result=row['result'];assert result['surfaces']==len(ranges) and result['dirty']==len(ranges) and result['downloaded']==len(ranges) and result['bytes']==sum(v[1] for v in ranges)
  assert not result['error'] and not result['reason'] and not result['old_halt'] and not result['consume_stop'] and not result['consume_words'] and not result['consume_steps']
  assert result['request']==result['gate']==t['current_fifo'][4:14] and not result['wait_before'] and not result['wait_after']
  row['worker_full_byte_comparison_passed']=True;save()
 else:
  # Same bounded CPU-stopped RAM observations; no preservation request.
  row['control_no_request_verified']=True;save()
 if case=='preserve001':
  reply=cmd('qom-get '+path+' xwn-inventory242-report')
  paired=inventory_tuple(reply)
  row['paired_inventory_reply']=reply;row['paired_inventory']=paired;save()
  repeat=cmd('qom-get '+path+' xwn-inventory242-report')
  row['paired_inventory_immutable']=repeat==reply;save();assert repeat==reply
  row['paired_inventory_result']=inventory_qualify(paired,t);save()
  # No pmemsave: it dispatches GPU CPU-access callbacks and would change state.
 row['closed']=True;row['preservation_scope_passed']=case=='preserve001' and row.get('worker_full_byte_comparison_passed',False)
 r['dirty_surface_coverage']=row['preservation_scope_passed'];save()

try:
 deadline=time.monotonic()+45
 while not (run/'startup-ready.json').exists():
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists();time.sleep(.1)
 r['dashboard_barrier']=wait_dashboard(deadline);lock=acquire_monitor_lock(4594)
 cmd('stop');stopped=True;g=Remote(4595);r['features']=ask('qSupported');r['initial_stop']=ask('?')
 r['prior_physical_mode']=ask('qqemu.PhyMemMode');assert r['prior_physical_mode']=='0';r['physical_mode_restored']=True
 overall=time.monotonic()+120
 inventory=read(k/'inventory001.json');r['inventory_sha256']=sha(k/'inventory001.json');r['capstone_version']=capstone.__version__
 if phase=='dashboard':take_snapshot('dashboard_cpu_stop',regs())
 launcher=inventory['launcher'];freeldr=inventory['freeldr'];entry=launcher['entry'];mbentry=int(freeldr['entry_address'],16)
 arm(0,entry,1)
 # Trace, not supervisor, owns the one authorized loopback launch.
 row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');r['loader_launch']=row;save()
 g.send('c');stopped=False
 with DeadlineFTP(time.monotonic()+6) as ftp:
  ftp.connect('127.0.0.1',4596,timeout=ftp.budget());ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
  row['reply']=ftp.sendcmd(row['command']);row['status']='accepted';save()
 g.s.settimeout(20)
 try:reply=g.recv();stopped=True
 except socket.timeout:g.s.settimeout(5);g.interrupt();stopped=True;raise AssertionError('XBE entry stop bound')
 finally:g.s.settimeout(5)
 values=regs();assert values[8]==entry,(reply,values)
 data,pin=resident('xbe-entry',entry,32);expected=span((k/'artifacts/inputs/xromwell.xbe').read_bytes(),launcher,entry,32)
 r['events'].append(dict(name='actual_xromwell_xbe_entry',stop=reply,registers=values,pin=pin,expected_sha256=hashlib.sha256(expected).hexdigest(),resident_bytes_match=data==expected));save();assert data==expected
 if phase=='xbe':
  take_snapshot('actual_xromwell_xbe_entry',values)
  response=cmd('qom-set '+r['nv2a_qom_path']+' xwn-lifecycle244-mark true');assert 'Error' not in response
  preservation_experiment()
 remove((0,entry,1));arm(0,mbentry,1);reply=continue_stop(20);values=regs();assert values[8]==mbentry,(reply,values)
 data,pin=resident('freeldr-multiboot-entry',mbentry,32);raw=(k/'artifacts/inputs/freeldr.sys').read_bytes();offset=mbentry-int(freeldr['staging_address'],16);expected=raw[offset:offset+32];assert len(expected)==32
 r['events'].append(dict(name='actual_freeldr_multiboot_entry',stop=reply,registers=values,pin=pin,expected_sha256=hashlib.sha256(expected).hexdigest(),resident_bytes_match=data==expected));save();assert data==expected
 # Close actual UI admission at pinned FreeLoader; no synchronous QOM wait.
 frontend_requested=True
 r['frontend_close_request_may_be_accepted']=True;save()
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close true');assert 'Error' not in reply
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
  state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
  if state in [2,3]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['frontend_closed_report']=reply;save()
 assert state==2,'Explicit bounded UI close refusal, never retry'
 assert ' loan=0 ' in reply and ' bql=0 ' in reply and ' error=0 ' in reply
 # Worker admission is separate. Request while CPU stopped/UI acknowledged.
 worker_requested=True;r['worker_request_may_be_accepted']=True;save()
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close true');assert 'Error' not in reply
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
  state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
  if state in [3,5,6]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['worker_closed_report']=reply;save()
 assert state==3,'Worker explicitly refused/expired; preserve evidence, never retry'
 time.sleep(.2)
 r['worker_closed_reread']=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report');save()
 assert r['worker_closed_reread']==reply
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close false');assert 'Error' not in reply
 worker_released=True;r['worker_release_requested']=True;save()
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
  state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
  if state in [5,6]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['worker_released_report']=reply;save();assert state==5
 r['worker_scope_passed']=True;save()
 # No new frame may start throughout this interval. Keep all shared objects.
 time.sleep(.2)
 r['frontend_closed_reread']=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report');save()
 assert r['frontend_closed_reread']==r['frontend_closed_report']
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close false');assert 'Error' not in reply
 frontend_reopened=True;r['frontend_reopen_requested']=True;save()
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
  state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
  if state==5:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['frontend_reopened_report']=reply;r['frontend_scope_passed']=True;save()
 # Existing CPU-exclusive queue may run while stopped. No wait under actor locks.
 time.sleep(.2)
 response=cmd('qom-set '+r['nv2a_qom_path']+' xwn-lifecycle244-mark true');assert 'Error' not in response
 for event in ['xwn_mem_callback244','nv2a_lifecycle244']:
  response=cmd('trace-event '+event+' off');assert 'Error' not in response
 r['lifecycle_window_closed']=True;save()
 if phase=='freeldr':take_snapshot('actual_freeldr_multiboot_entry',values)
 remove((0,mbentry,1));r.update(passed=True,status='phase_snapshot_and_actual_loader_entries_observed');save()
except BaseException as exc:r.update(status='preserved_guest_trace_failure',error=repr(exc),host_traceback=traceback.format_exc());save()
finally:
 if r.get('preservation',{}).get('request_may_be_accepted') and r['preservation'].get('terminal_state') not in [3,4]:
  quarantined=True;r['preservation']['unknown_or_unsafe_terminal_quarantined']=True;save()
 if worker_requested and not r.get('worker_scope_passed'):
  try:
   reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
   state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
   if state in [1,2,3] and not worker_released:
    reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-worker247-close false')
    r['worker_failure_release_reply']=reply;worker_released='Error' not in reply
   deadline=time.monotonic()+8
   while True:
    reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-worker247-report')
    state=int(re.search(r'(?<![a-z_])state=(\d+)',reply)[1])
    r['worker_failure_terminal']=reply;save()
    if state in [0,5,6]:break
    assert time.monotonic()<deadline;time.sleep(.025)
   r['worker_failure_released_or_refused']=True
  except Exception as exc:r['worker_failure_cleanup_error']=repr(exc);quarantined=True
 if frontend_requested and not frontend_reopened:
  try:
   reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close false')
   r['frontend_failure_reopen_reply']=reply;frontend_reopened='Error' not in reply
   if not frontend_reopened:quarantined=True
  except Exception as exc:r['frontend_failure_reopen_error']=repr(exc);quarantined=True
 if frontend_requested and frontend_reopened and not r.get('frontend_scope_passed'):
  try:
   deadline=time.monotonic()+8
   while True:
    reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
    r['frontend_failure_reopen_report']=reply;save()
    if re.search(r'(?<![a-z_])state=5(?:[, ]|$)',reply):break
    assert time.monotonic()<deadline;time.sleep(.025)
   r['frontend_failure_reopen_acknowledged']=True
  except Exception as exc:r['frontend_failure_reopen_ack_error']=repr(exc);quarantined=True
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as exc:r['interrupt_error']=repr(exc);quarantined=True
  if stopped:
   for item in armed.copy():
    try:remove(item)
    except Exception as exc:r['point_cleanup_error']=repr(exc);quarantined=True
   try:
    if ask('qqemu.PhyMemMode')!='0':quarantined=True;r['physical_mode_restored']=False
   except Exception as exc:
    r['mode_verification_error']=repr(exc);r['physical_mode_restored']=False;quarantined=True
   if quarantined:
    r['guest_resumed']=False;r['quarantine_retained_until_owned_process_exit']=True
    try:cmd('quit')
    except Exception as exc:r['quit_reply_error']=repr(exc)
   else:
    try:g.send('c');stopped=False;r['guest_resumed']=True
    except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 if lock:lock.close()
 r.update(remaining_breakpoints=armed.copy(),closed=True,closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','guest_resumed','error'] if n in r}))
