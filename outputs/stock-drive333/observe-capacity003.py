"""Control-channel-only, single emulator SITE; collect report cold later."""
import ftplib,json,os,sys,time,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'capacity-emu003';run=Path('E:/xwn333/runs/nt5-capacity333-emu003')
sys.path.insert(0,str(K.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
dest=out/'launch.json';assert not dest.exists()
r=dict(physical_access=False,launch_requested=False,dashboard_return=False,offline_observed=False)
save=lambda:write_json(dest,r)
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+4))
    try:f.connect('127.0.0.1',5118,timeout=f.budget());f.login('xbox','xbox');return f
    except Exception:f.close();raise
try:
    save();deadline=time.monotonic()+70
    while True:
        try:f=connect(deadline);break
        except ftplib.all_errors:
            if time.monotonic()>=deadline:raise
            time.sleep(1)
    assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
    r.update(launch_requested=True,requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNCapacity333\default.xbe');save()
    try:
        try:r['reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as e:r['reply_uncertain']=type(e).__name__
    finally:f.close();save()
    deadline=time.monotonic()+90
    while time.monotonic()<deadline and not (run/'cleanup.json').exists():
        time.sleep(.5)
        try:
            f=connect(deadline);f.close()
            if r['offline_observed']:
                r.update(dashboard_return=True,returned_utc=utc());break
        except ftplib.all_errors:r['offline_observed']=True
    save()
except BaseException as e:r['error']=repr(e);save();raise
finally:
    if run.exists() and not (run/'cleanup.json').exists():(run/'capture-complete.signal').touch(exist_ok=False)
    r['observer_closed']=True;save();print(json.dumps(r,indent=2))
