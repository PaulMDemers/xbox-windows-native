"""Wait for cooperative resources, then one launch/observer/cold audit per fresh case."""
import datetime,hashlib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['trace001']
out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/handoff225-runs/nt5-handoff225-'+case)
dest=out/'host-state.json';assert not dest.exists() and not (out/'runner-start.json').exists() and not run.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h

child=None;observer=None;tracer=None
r=dict(case=case,controller_pid=os.getpid(),source_sha256=sha(Path(__file__)),physical_access=False,debugger=True,resource_attempts=[],closed=False)
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n');temp.replace(dest)
def launch(argv,log):
 return subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
try:
 deadline=time.monotonic()+900;attempt=0
 while True:
  attempt+=1;p=out/('resource-attempt%d-console.txt'%attempt)
  with p.open('x',encoding='utf-8') as log:
   child=launch(['pwsh','-NoProfile','-File',str(k/'Run.ps1'),'-Case',case],log)
   r.update(runner_pid=child.pid,status='waiting_for_owned_run');save()
   while child.poll() is None and not (run/'instance.json').exists():time.sleep(.5)
   if (run/'instance.json').exists():break
   code=child.wait();text=p.read_text(encoding='utf-8')
   busy="Xbox resource 'build' is busy or unavailable" in text or "Xbox resource 'xemu' is busy or unavailable" in text
   row=dict(attempt=attempt,exit_code=code,utc=utc(),resource_busy=busy,log_sha256=sha(p),runner_start_exists=(out/'runner-start.json').exists(),run_exists=run.exists())
   r['resource_attempts'].append(row);save()
   assert busy and not row['runner_start_exists'] and not row['run_exists'],'Preserve failed start; never retry after resource acquisition/run creation'
   assert time.monotonic()<deadline,'Resource wait bound; no guest launched'
   time.sleep(15)
 # The still-open runner console stream is intentionally retained until exit.
 r.update(status='single_runner_active',instance_sha256=sha(run/'instance.json'));save()
 with (out/'tracer-console.txt').open('x',encoding='utf-8') as tracer_log:
  tracer=launch([sys.executable,str(k/'trace.py'),case],tracer_log)
  r.update(tracer_pid=tracer.pid);save()
 with (out/'observer-console.txt').open('x',encoding='utf-8') as observer_log:
  observer=launch([sys.executable,str(k/'supervise-emulator.py'),case],observer_log)
  r.update(observer_pid=observer.pid);save();observer_code=observer.wait(timeout=610)
 r.update(observer_exit_code=observer_code,runner_exit_code=child.wait(timeout=60),status='closed_pending_cold_audit');save()
 assert (run/'cleanup.json').exists(),'Owned cleanup required before cold inspection'
 r['tracer_exit_code']=tracer.wait(timeout=15);save()
 linux='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/video-loader-handoff225/audit-emulator.py'
 with (out/'cold-audit-console.txt').open('x',encoding='utf-8') as audit_log:
  code=subprocess.run(['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3',linux,case],stdout=audit_log,stderr=subprocess.STDOUT).returncode
 r.update(audit_exit_code=code,status='cold_audited_closed' if code==0 else 'cold_audit_failed_preserved');save()
 assert code==0
 r['cpu_scope_passed']=read(out/'audit.json')['cpu_scope_passed'];r['observation_scope_passed']=read(out/'audit.json')['observation_scope_passed']
except Exception as exc:
 r.update(status='preserved_failure',error=repr(exc));save();raise
finally:
 # Do not mark a living owned guest closed on a controller failure. The runner
 # retains its own480-second bound and finally cleanup. Preserve actual state.
 if observer is not None and observer.poll() is None:
  observer.terminate();observer.wait(timeout=10)
 if child is not None and child.poll() is None:
  try:child.wait(timeout=510)
  except subprocess.TimeoutExpired:r['owned_runner_still_active']=True
 if tracer is not None and tracer.poll() is None:
  try:tracer.wait(timeout=210)
  except subprocess.TimeoutExpired:r['owned_tracer_still_active']=True
 closed=(child is None or child.poll() is not None) and (tracer is None or tracer.poll() is not None)
 r.update(closed=closed,cleanup_record_exists=(run/'cleanup.json').exists(),closed_utc=utc() if closed else None);save()
print(json.dumps(r,indent=2))
