"""One owned diagnostic launch, bounded trace/return observation, one cold audit."""
import ast,datetime,ftplib,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu001'
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/pending263/runs/nt5-pending263-emu001')
dest=out/'host-state.json';assert not dest.exists() and not run.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in json.loads((k/'emulator-frozen.json').read_text()).items():assert sha(ws/n)==h,n
assert json.loads((k/'runtime-review.json').read_text())['passed']
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
tree=ast.parse((k.parent/'native-windows-prebuild/launch_unleashx.py').read_text())
login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
for name,arg in zip(['XWN_EMULATOR_FTP_USER','XWN_EMULATOR_FTP_PASSWORD'],login.args):os.environ.setdefault(name,ast.literal_eval(arg))
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(closed=False,physical_access=False,debugger=True,status='starting',started_utc=utc())
def save():
 write_json(dest,r)
runner=tracer=None;save()
try:
 with (out/'runner-console.txt').open('x') as log:
  runner=subprocess.Popen(['pwsh','-NoProfile','-File',str(k/'Run.ps1')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 r['runner_pid']=runner.pid;save();deadline=time.monotonic()+180
 while not (run/'startup-ready.json').exists():
  assert runner.poll() is None and time.monotonic()<deadline,'No owned ready instance; preserve start failure'
  time.sleep(.5)
 with (out/'trace-console.txt').open('x') as log:
  tracer=subprocess.Popen([sys.executable,'-B',str(k/'trace.py')],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 r.update(tracer_pid=tracer.pid,status='single_diagnostic_run');save()
 r['tracer_exit_code']=tracer.wait(timeout=330);save()
 trace=json.loads((out/'trace.json').read_text());assert trace['closed']
 launch=dict(cycles=[dict(trace.get('launch',{}),dashboard_return=False)],physical_access=False,debugger=True)
 if trace['passed'] and trace.get('guest_resumed'):
  r['status']='waiting_one_normal_return';save();deadline=time.monotonic()+150
  while time.monotonic()<deadline and not (run/'cleanup.json').exists():
   try:
    with DeadlineFTP(time.monotonic()+4) as ftp:
     ftp.connect('127.0.0.1',4596,timeout=ftp.budget());ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);ftp.sendcmd('NOOP')
    launch['cycles'][0].update(dashboard_return=True,dashboard_return_utc=utc())
    (run/'capture-complete.signal').touch(exist_ok=False);break
   except ftplib.all_errors:time.sleep(1)
 else:r['status']='diagnostic_failure_quarantined';save()
 (out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n')
 r['runner_exit_code']=runner.wait(timeout=120);save()
 assert (run/'cleanup.json').exists(),'Closed guest required before audit'
 linux='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/surface-pending263/audit.py'
 with (out/'audit-console.txt').open('x') as log:
  r['audit_exit_code']=subprocess.run(['wsl','-d','Ubuntu','--','env','LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu','python3',linux,'emu001'],stdout=log,stderr=subprocess.STDOUT).returncode
 r['status']='cold_audited' if r['audit_exit_code']==0 else 'cold_audit_failure';save()
except BaseException as e:r.update(error=repr(e),status='preserved_failure');save();raise
finally:
 if tracer is not None and tracer.poll() is None:
  r['tracer_still_active']=True;save()
 if runner is not None and runner.poll() is None:
  r['owned_runner_still_active']=True;save()
 r.update(closed=runner is None or runner.poll() is not None,finished_utc=utc(),cleanup_record_exists=(run/'cleanup.json').exists());save()
print(json.dumps(r,indent=2))
