"""One ordinary launch; dashboard return or bounded owned host closure, no relaunch."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'cancel001';run=ws/'work/runs/nt5-wizard201-cancel001'
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
dest=out/'launch.json';assert not dest.exists() and (run/'instance.json').exists() and not (run/'cleanup.json').exists()
r=dict(run=run.name,host='127.0.0.1',port=4596,debugger=False,physical_access=False,cycles=[])
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');temp.replace(dest)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+6))
    try:f.connect('127.0.0.1',4596,timeout=f.budget());f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
    except Exception:f.close();raise
deadline=time.monotonic()+60
while True:
    try:f=connect(deadline);break
    except ftplib.all_errors:
        if time.monotonic()>=deadline:raise
        time.sleep(1)
assert not (run/'cleanup.json').exists()
row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe')
r['cycles'].append(row);save()
try:
    try:row.update(reply=f.sendcmd(row['command']),status='accepted')
    except ftplib.all_errors as exc:row.update(status='reply_uncertain',error=type(exc).__name__)
    save()
finally:f.close()
print('One targeted cancellation201 launch; never relaunch',flush=True)
deadline=time.monotonic()+340;offline=False
while time.monotonic()<deadline:
    if (run/'cleanup.json').exists():
        row.update(offline_observed=offline,dashboard_return=False,owned_closure_observed_utc=utc())
        r['status']='owned_host_bound_closed_pending_cold_audit';save();break
    time.sleep(2)
    try:
        f=connect(deadline);f.close()
        if offline:
            row.update(offline_observed=True,dashboard_return=True,dashboard_return_utc=utc())
            assert not (run/'cleanup.json').exists()
            r['status']='return_pending_cold_audit';save();(run/'capture-complete.signal').touch(exist_ok=False);break
    except ftplib.all_errors:offline=True
else:
    r['status']='observer_deadline';save();raise RuntimeError('Owned runner did not close within its bound; inspect, never relaunch')
print(r['status'],flush=True)
