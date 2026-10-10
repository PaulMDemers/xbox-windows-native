"""One owned executable-pinned loader stop and opt-in backend preservation."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/reason228-runs/nt5-reason228-'+case)
assert (run/'instance.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
iv=read(k.parent/'video-loader-handoff225/inventory002.json');site=iv['sites']['producer_exit_entry']
raw=ws/iv['binaries']['image-crom.bin']['path'];assert sha(raw)==iv['binaries']['image-crom.bin']['sha256'];raw=raw.read_bytes()
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
 lock=acquire_monitor_lock(4594);cmd('stop');stopped=True
 g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 assert 'state=0' in cmd('qom-get '+path+' xwn-preserve227-report')
 g.bp(site);armed=True;g.send('c');stopped=False;save();(out/'trace-armed.signal').touch(exist_ok=False)
 deadline=time.monotonic()+180
 while True:
  g.s.settimeout(2)
  try:reply=g.recv();break
  except TimeoutError:
   if time.monotonic()>=deadline:g.s.settimeout(5);g.interrupt();stopped=True;raise TimeoutError('Loader boundary deadline')
 stopped=True;g.s.settimeout(5)
 vals=struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40]);assert vals[8]==site
 actual=g.read(site,64);expected=raw[site-0x3a00000:site-0x3a00000+64];assert actual==expected
 r['executing_code_pin']=dict(address=site,bytes=64,hex=actual.hex(),sha256=hashlib.sha256(actual).hexdigest(),registers=vals,stop_reply=reply)
 g.bp(site,False);armed=False
 r['before']=snapshot('before');save()
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
 r['preserve_result']={n:int(v) for n,v in re.findall(r'(state|surfaces|dirty|downloaded|bytes|error|reason|references_retired|native_grant)=(\d+)',report)}
 assert r['preserve_result']['native_grant']==r['preserve_result']['references_retired']==0
 quarantined=state in [5,6]
 r['after']=snapshot('after');r['reserved_bytes_unchanged']=all(a['sha256']==b['sha256'] for a,b in zip(r['before'],r['after']))
 r['dirty_surface_coverage']=state==3 and r['preserve_result']['dirty']>0 and r['preserve_result']['downloaded']==r['preserve_result']['dirty'] and r['preserve_result']['bytes']>0
 r.update(passed=state==3 and r['reserved_bytes_unchanged'],status='preserved_with_dirty_coverage' if r['dirty_surface_coverage'] else 'no_dirty_coverage_or_refused',request_terminal=True);save()
except BaseException as exc:r.update(status='preserved_trace_failure',error=repr(exc),host_traceback=traceback.format_exc());save()
finally:
 if g:
  if not stopped:
   try:g.s.settimeout(5);g.interrupt();stopped=True
   except Exception as exc:r['interrupt_error']=repr(exc)
  if stopped:
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
