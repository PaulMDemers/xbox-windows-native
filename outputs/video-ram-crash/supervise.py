"""Launch exactly once over local emulator FTP; await trace, then preserve crash."""
import datetime,ftplib,json,os,subprocess,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001';run=ws/'work/runs/nt5-video-ram-crash-crash001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
assert (out/'trace-armed.signal').exists() and not (out/'launch.json').exists()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(physical_access=False,host='127.0.0.1',port=4596,intentional_crash=True,ordinary_qualified=False,prelaunch_errors=[])
def save():write_json(out/'launch.json',r)
deadline=time.monotonic()+60
while True:
    f=ftplib.FTP()
    try:f.connect('127.0.0.1',4596,timeout=3);f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);break
    except ftplib.all_errors as exc:
        f.close();r['prelaunch_errors'].append(type(exc).__name__)
        if time.monotonic()>=deadline:save();raise
        time.sleep(2)
r.update(status='requesting',launch_requested_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save()
try:
    try:r.update(reply=f.sendcmd(r['command']),status='accepted')
    except ftplib.all_errors as exc:r.update(status='reply_uncertain',error=type(exc).__name__)
finally:f.close();save()
print(json.dumps(r),flush=True)
deadline=time.monotonic()+660
while not (out/'trace-finished.signal').exists():
    assert not (run/'cleanup.json').exists()
    if time.monotonic()>=deadline:raise RuntimeError('Observer did not finish; inspect owned session')
    time.sleep(3)
r['trace_finished_utc']=utc();save()
# The dump routine returned or tracing failed. Allow final output without reboot.
time.sleep(30)
capture=[os.sys.executable,str(k.parent/'native-windows-prebuild/monitor_capture.py'),'--port','4594','--output',str(out/'artifacts/crash.png'),'--width','1024','--height','576','--pitch','4096','--auto-framebuffer']
r['capture_exit']=subprocess.run(capture,check=False).returncode;r['capture_utc']=utc();save()
r['cleanup_requested_utc']=utc();r['status']='single_crash_closed_pending_cold_audit';save();(run/'capture-complete.signal').touch(exist_ok=False)
