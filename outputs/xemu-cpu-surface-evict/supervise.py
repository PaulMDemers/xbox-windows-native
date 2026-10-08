"""Launch the native app exactly once via emulator loopback, then observe return."""
import datetime,ftplib,json,os,time,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control002','candidate002']
out=k/case;run=k.parents[1]/('work/runs/gpu-evict-'+case)
p=out/'launch.json';assert not p.exists()
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
r=dict(physical_access=False,host='127.0.0.1',port=4596,command=r'SITE EXEC E:\Applications\XWNGpu144\default.xbe')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n');temp.replace(p)
def connect():
    f=ftplib.FTP()
    try:
        f.connect('127.0.0.1',4596,timeout=3)
        f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
        return f
    except Exception:f.close();raise
deadline=time.monotonic()+60
while True:
    assert not (run/'cleanup.json').exists()
    try:f=connect();break
    except ftplib.all_errors:
        if time.monotonic()>deadline:raise
        time.sleep(2)
r.update(requested_utc=utc(),status='requesting',trace_before_launch=(run/'cpu-trace.log').stat().st_size);save()
try:
    try:r.update(reply=f.sendcmd(r['command']),status='accepted')
    except ftplib.all_errors as e:r.update(status='reply_uncertain',error=type(e).__name__)
finally:f.close()
save();print('One native GPU probe requested; no Windows launch',flush=True)
deadline=time.monotonic()+280;offline=False
while time.monotonic()<deadline:
    if (run/'cleanup.json').exists():break
    time.sleep(2)
    try:
        f=connect()
        try:
            if offline:
                r.update(dashboard_return=True,returned_utc=utc(),offline_observed=True,
                         collection='Authoritative offline disk audit; no FTP data channel')
                save()
                (run/'capture-complete.signal').touch(exist_ok=False)
                print('Dashboard returned; cold audit pending',flush=True);break
        finally:f.close()
    except ftplib.all_errors:offline=True
else:
    r.update(dashboard_return=False,offline_observed=offline,status='timeout');save()
    raise RuntimeError('No observed return; no relaunch')
