"""One ordinary CPU-only arena boot, owned closure and first cold audit."""
import datetime,hashlib,json,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu001'
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/pattern258/runs/nt5-pattern258-emu001')
dest=out/'host-state.json';assert not dest.exists() and not run.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((k/'emulator-frozen.json').read_text()).items():assert sha(ws/n)==h,n
assert json.loads((k/'runtime-review.json').read_text())['passed']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(closed=False,physical_access=False,debugger=False,status='starting',started_utc=utc())
def save():
 p=dest.with_suffix('.tmp');p.write_text(json.dumps(r,indent=2)+'\n');p.replace(dest)
runner=observer=None;save()
try:
 with (out/'runner-console.txt').open('x') as log:
  runner=subprocess.Popen(['pwsh','-NoProfile','-File',str(k/'Run.ps1')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 r['runner_pid']=runner.pid;save();deadline=time.monotonic()+180
 while not (run/'instance.json').exists():
  assert runner.poll() is None and time.monotonic()<deadline,'No owned instance; preserve start failure'
  time.sleep(.5)
 with (out/'observer-console.txt').open('x') as log:
  observer=subprocess.Popen([sys.executable,'-B',str(k/'supervise.py'),'emu001'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 r.update(observer_pid=observer.pid,status='single_ordinary_run');save()
 r['observer_exit_code']=observer.wait(timeout=660);r['runner_exit_code']=runner.wait(timeout=90);save()
 assert (run/'cleanup.json').exists(),'Closed guest required before audit'
 linux='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/surface-pattern258/audit.py'
 with (out/'audit-console.txt').open('x') as log:
  r['audit_exit_code']=subprocess.run(['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3',linux,'emu001'],stdout=log,stderr=subprocess.STDOUT).returncode
 r['status']='cold_audited' if r['audit_exit_code']==0 else 'cold_audit_failure';save()
except Exception as exc:r.update(error=repr(exc),status='preserved_failure');save();raise
finally:
 if observer is not None and observer.poll() is None:observer.terminate();observer.wait(timeout=15)
 if runner is not None and runner.poll() is None:
  try:runner.wait(timeout=620)
  except subprocess.TimeoutExpired:r['owned_runner_still_active']=True
 r.update(closed=runner is None or runner.poll() is not None,finished_utc=utc(),cleanup_record_exists=(run/'cleanup.json').exists());save()
print(json.dumps(r,indent=2))
