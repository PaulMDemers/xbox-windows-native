"""One local emulator FTP launch, bounded trace wait, screenshot and owned closure."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];out=k/case
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/reset221-runs/nt5-reset221-'+case)
assert not (out/'launch.json').exists() and (run/'instance.json').exists() and not (run/'cleanup.json').exists()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(physical_access=False,host='127.0.0.1',port=4596,intentional_crash=True,ordinary_qualified=False,prelaunch_errors=[])
def save():
 p=out/'launch.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'launch.json')
try:
 deadline=time.monotonic()+60
 while True:
  f=ftplib.FTP()
  try:f.connect('127.0.0.1',4596,timeout=3);f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);break
  except ftplib.all_errors as exc:
   f.close();r['prelaunch_errors'].append(type(exc).__name__)
   if time.monotonic()>=deadline:raise
   time.sleep(2)
 r.update(status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save()
 try:
  try:r.update(reply=f.sendcmd(r['command']),status='accepted')
  except ftplib.all_errors as exc:r.update(status='reply_uncertain',error=type(exc).__name__)
 finally:f.close();save()
 deadline=time.monotonic()+460
 while not (out/'trace-finished.signal').exists():
  assert not (run/'cleanup.json').exists()
  if time.monotonic()>=deadline:raise TimeoutError('Owned trace deadline; never relaunch')
  time.sleep(2)
 r['trace_finished_utc']=utc();save()
 # Crash callbacks may fail on inherited0101. Capture actual later state, no
 # dump-completion or clean-shutdown inference from the rendering result.
 time.sleep(15)
 capture=[sys.executable,str(ws/'outputs/native-windows-prebuild/monitor_capture.py'),'--port','4594','--output',str(out/'artifacts/crash.png'),'--width','1024','--height','576','--pitch','4096','--auto-framebuffer']
 r['capture_exit']=subprocess.run(capture,check=False).returncode;r['status']='single_crash_closed_pending_cold_audit';save()
except Exception as exc:r.update(error=repr(exc),status='preserved_supervisor_failure');save();raise
finally:
 r['cleanup_requested_utc']=utc();save()
 if not (run/'cleanup.json').exists() and not (run/'capture-complete.signal').exists():(run/'capture-complete.signal').touch(exist_ok=False)
print(json.dumps(r,indent=2))
