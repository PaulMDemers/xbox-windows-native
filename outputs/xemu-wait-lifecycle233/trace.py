"""One owned pre-loader dashboard stop and compiled-model diagnostic."""
import datetime,ftplib,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/wait233-runs/nt5-wait233-'+case)
assert (run/'instance.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
site=None # No guest breakpoint or native executing-code source pin.
r=dict(scope=__doc__,debugger=True,physical_access=False,gpu_ownership_qualified=False,ordinary_qualified=False,debugger_memory_writes=False,passed=False,dirty_surface_coverage=False,started_utc=utc(),monitor=[])
g=None;lock=None;armed=False;stopped=False;quarantined=False
def save():
 p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def cmd(s):
 value=command(4594,s);r['monitor'].append(dict(utc=utc(),command=s,reply=value));save();return value
def qom_path(tree):
 stack=[];found=[]
 for line in tree.splitlines():
  m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
  if not m:continue
  level=len(m[1]);name=m[2]
  while stack and stack[-1][0]>=level:stack.pop()
  if name:stack.append((level,name))
  if m[3]=='nv2a':found.append('/'+'/'.join(v for _,v in stack))
 assert len(found)==1,found;return found[0]
def wait_report(path):
 # Read-only try-lock contention retries, bounded; never repeats a request.
 deadline=time.monotonic()+1;attempts=0
 while True:
  attempts+=1;reply=cmd('qom-get '+path+' xwn-wait233-report')
  if 'busy=1' not in reply:return dict(reply=reply,attempts=attempts)
  assert time.monotonic()<deadline,'Read-only observer lock contention bound'
  time.sleep(.025)

def wait_dashboard(deadline):
 attempts=0
 while True:
  attempts+=1
  try:
   with DeadlineFTP(min(deadline,time.monotonic()+6)) as ftp:
    ftp.connect('127.0.0.1',4596,timeout=ftp.budget())
    ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
    return dict(utc=utc(),reply=ftp.sendcmd('NOOP'),attempts=attempts,physical_access=False)
  except ftplib.all_errors:
   if time.monotonic()>=deadline:raise
   time.sleep(min(.2,max(0,deadline-time.monotonic())))

def restore_physical_mode(remote,record):
 if not record.get('physical_mode_restore_required'):return True
 try:
  ok=remote.ask('Qqemu.PhyMemMode:0')=='OK' and remote.ask('qqemu.PhyMemMode')=='0'
  record['physical_mode_restored']=ok
  if ok:
   record['physical_read_mode']=False
   record['physical_mode_restore_required']=False
  return ok
 except Exception as exc:
  record['physical_mode_restore_error']=repr(exc)
  record['physical_mode_restored']=False
  return False

def snapshot(label):
 result=[]
 for name,a,n in [('ramin20k',0xfd710000,0x5000),('reserved_tail84k',0x03feb000,0x15000)]:
  data=b''.join(g.read(a+i,min(1024,n-i)) for i in range(0,n,1024));p=out/'artifacts'/(label+'-'+name+'.bin');p.write_bytes(data)
  result.append(dict(path=str(p.relative_to(ws)).replace('\\','/'),address=a,bytes=n,sha256=sha(p)))
 return result
try:
 deadline=time.monotonic()+45
 while not (run/'startup-ready.json').exists():
  assert time.monotonic()<deadline and not (run/'cleanup.json').exists();time.sleep(.1)
 sys.path.insert(0,str(k.parent/'gpu-reset-banner152'))
 from ftp_deadline import DeadlineFTP
 import os
 r['dashboard_barrier']=wait_dashboard(deadline)
 lock=acquire_monitor_lock(4594)
 # Two fixed read-only live observations, NOT a retry for an empty queue.
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 r['wait_live_first']=wait_report(path);save();time.sleep(.25)
 r['wait_live_second']=wait_report(path);save()
 cmd('stop');stopped=True
 g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 r['prior_physical_mode']=g.ask('qqemu.PhyMemMode');assert r['prior_physical_mode']=='0'
 r['physical_mode_restore_required']=True # Command/reply may be uncertain.
 assert g.ask('Qqemu.PhyMemMode:1')=='OK';r['physical_read_mode']=True
 assert g.ask('qqemu.PhyMemMode')=='1'
 r['observed_cpu_registers']=struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])
 r['phase']='dashboard before only Windows launch; observed CPU registers, no native code source pin'
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 assert 'state=0' in cmd('qom-get '+path+' xwn-preserve227-report')
 r['wait_stopped_before']=wait_report(path);r['before']=snapshot('before');save()
 # Unknown request/reply state is quarantined too; never resume on a host error
 # after the request might have been accepted.
 quarantined=True;r['request_may_be_accepted']=True;save()
 response=cmd('qom-set '+path+' xwn-preserve227 true')
 assert 'Error' not in response and 'busy' not in response and 'needs' not in response,response
 deadline=time.monotonic()+12
 while True:
  report=cmd('qom-get '+path+' xwn-preserve227-report');m=re.search(r'state=(\d+)',report);assert m,report
  state=int(m[1])
  if state in [3,4,5,6]:break
  assert time.monotonic()<deadline,'Host diagnostic wait deadline';time.sleep(.05)
 r['preserve_result']={n:int(v) for n,v in re.findall(r'(state|tuple_published|publication_version|surfaces|dirty|downloaded|bytes|error|reason|references_retired|native_grant|old_halt|consume_stop|consume_steps|consume_words|wait_before|wait_after|request[0-9]|gate[0-9])=(\d+)',report)}
 assert r['preserve_result']['publication_version']==232
 assert r['preserve_result']['tuple_published']==int(state in [3,4,6])
 assert r['preserve_result']['native_grant']==r['preserve_result']['references_retired']==0
 quarantined=state in [5,6]
 r['wait_stopped_after']=wait_report(path);r['after']=snapshot('after');r['reserved_bytes_unchanged']=all(a['sha256']==b['sha256'] for a,b in zip(r['before'],r['after']))
 # Real command consumption can write backing state. Until those writes are
 # independently attributed, changes in either reserved range quarantine.
 if not r['reserved_bytes_unchanged']:quarantined=True
 r['dirty_surface_coverage']=state==3 and r['preserve_result']['dirty']>0 and r['preserve_result']['downloaded']==r['preserve_result']['dirty'] and r['preserve_result']['bytes']>0
 r.update(passed=state==3 and r['reserved_bytes_unchanged'],status='preserved_with_dirty_coverage' if r['dirty_surface_coverage'] else 'no_dirty_coverage_or_refused',request_terminal=True);save()
except BaseException as exc:r.update(status='preserved_trace_failure',error=repr(exc),host_traceback=traceback.format_exc());save()
finally:
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as exc:r['interrupt_error']=repr(exc)
  if stopped:
   if not restore_physical_mode(g,r):quarantined=True
   if armed:
    try:g.bp(site,False);armed=False
    except Exception as exc:r['breakpoint_cleanup_error']=repr(exc)
   if quarantined:
    r['guest_resumed']=False;r['quarantine_retained_until_owned_process_exit']=True
    try:cmd('quit')
    except Exception as exc:r['quit_reply_error']=repr(exc)
   else:
    try:g.send('c');stopped=False;r['guest_resumed']=True
    except Exception as exc:r['resume_error']=repr(exc)
  g.s.close()
 if lock:lock.close()
 r.update(remaining_breakpoints=[site] if armed else [],closed=True,closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','dirty_surface_coverage','preserve_result','guest_resumed','error'] if n in r}))
