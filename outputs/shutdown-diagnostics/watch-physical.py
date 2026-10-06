"""Observe the single diagnostic launch; never launch or repeat anything."""
import datetime,ftplib,json,os,time
from pathlib import Path
k=Path(__file__).resolve().parent;source=json.loads((k/'physical.json').read_text());assert source['launch_attempted'] and not source.get('collected_utc')
p=k/'physical-return.json';assert not p.exists()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,launch_utc=source['launch_utc'],started_utc=utc(),offline_observed=False,dashboard_return=False)
def save():p.write_text(json.dumps(r,indent=2)+'\n')
save();end=time.monotonic()+420
while time.monotonic()<end:
    f=ftplib.FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=3);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        if r['offline_observed']:r.update(dashboard_return=True,returned_utc=utc());save();print('Dashboard returned; collect once');break
    except ftplib.all_errors:
        if not r['offline_observed']:r.update(offline_observed=True,offline_utc=utc());save()
    finally:f.close()
    time.sleep(5)
else:r['timeout_utc']=utc();save();print('No dashboard return observed; screen unknown')
