"""Own one boot_guard223 runner/tracer/supervisor and collect once after closure."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control003','candidate003'];out=k/case
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/bootguard223-runs/nt5-bootguard223-'+case);dest=out/'host-state.json'
assert not dest.exists() and not (out/'runner-start.json').exists() and not run.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
for p,h in read(k/'frozen003.json').items():assert sha(ws/p)==h,p
if case=='candidate003':assert read(k/'control003/host-state.json')['closed']
r=dict(case=case,controller_pid=os.getpid(),physical_access=False,debugger=True,intentional_crash=False,ordinary_qualified=False,resource_attempts=[],closed=False)
children=[];streams=[]
def save():
 p=dest.with_suffix('.tmp');p.write_text(json.dumps(r,indent=2)+'\n');p.replace(dest)
def launch(argv,name):
 log=(out/name).open('x',encoding='utf-8');streams.append(log);p=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);children.append(p);return p
try:
 deadline=time.monotonic()+600;attempt=0
 while True:
  attempt+=1;name='resource-attempt%d-console.txt'%attempt;runner=launch(['pwsh','-NoProfile','-File',str(k/'Run003.ps1'),'-Case',case],name)
  r.update(runner_pid=runner.pid,status='waiting_for_resources');save()
  while runner.poll() is None and not (run/'instance.json').exists():time.sleep(.5)
  if (run/'instance.json').exists():break
  code=runner.wait();text=(out/name).read_text();busy="Xbox resource 'build' is busy or unavailable" in text or "Xbox resource 'xemu' is busy or unavailable" in text
  r['resource_attempts'].append(dict(exit_code=code,resource_busy=busy,log_sha256=sha(out/name)));save()
  assert busy and not (out/'runner-start.json').exists() and not run.exists(),'Do not retry a created or failed launch'
  assert time.monotonic()<deadline;time.sleep(10)
 ready_deadline=time.monotonic()+70
 while not (run/'monitor-ready.json').exists():
  assert runner.poll() is None and not (run/'cleanup.json').exists() and time.monotonic()<ready_deadline,'Runner failed before monitor ready; never launch'
  time.sleep(.2)
 ready=read(run/'monitor-ready.json');assert ready['network_enabled'] and ready['runner_source_sha256']==sha(k/'Invoke-223003.ps1')
 r['monitor_ready_sha256']=sha(run/'monitor-ready.json');save()
 tracer=launch([sys.executable,str(k/'trace003.py'),case],'trace-console.txt');supervisor=launch([sys.executable,str(k/'supervise003.py'),case],'supervisor-console.txt')
 r.update(status='single_boot_guard_run_active',tracer_pid=tracer.pid,supervisor_pid=supervisor.pid,instance_sha256=sha(run/'instance.json'));save()
 r['supervisor_exit']=supervisor.wait(timeout=500);r['tracer_exit']=tracer.wait(timeout=20);r['runner_exit']=runner.wait(timeout=50);save()
 assert (run/'cleanup.json').exists()
 script='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/video-boot-guard223/audit003.py'
 with (out/'audit-console.txt').open('x',encoding='utf-8') as log:
  r['audit_exit']=subprocess.run(['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3',script,case],stdout=log,stderr=subprocess.STDOUT).returncode
 r.update(status='cold_audited_closed' if r['audit_exit']==0 else 'cold_audit_failure_preserved');save()
except Exception as exc:r.update(error=repr(exc),status='preserved_controller_failure');save();raise
finally:
 if run.exists() and not (run/'cleanup.json').exists() and not (run/'capture-complete.signal').exists():(run/'capture-complete.signal').touch(exist_ok=False)
 # Do not kill a tracer with planted breakpoints: its bounded finally must run.
 for child in children:
  if child.poll() is None:
   try:child.wait(timeout=510)
   except subprocess.TimeoutExpired:r.setdefault('still_running_pids',[]).append(child.pid)
 for stream in streams:stream.close()
 r.update(closed=all(p.poll() is not None for p in children),closed_utc=utc());save()
print(json.dumps(r,indent=2))
