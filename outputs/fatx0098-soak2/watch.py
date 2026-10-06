"""Observe one recorded launch returning to dashboard; never launches anything."""
import argparse,ftplib,io,json,os,time
from physical import k,save,utc
p=argparse.ArgumentParser();p.add_argument('kind',choices=['windows','scan']);a=p.parse_args()
source=k/('physical.json' if a.kind=='windows' else 'scan.json');r=json.loads(source.read_text());assert r['launch_attempted'] and not r.get('collected_utc')
dest=k/(a.kind+'-return.json');assert not dest.exists(),'Inspect existing observation instead of overwriting it'
r=dict(scope=__doc__,kind=a.kind,started_utc=utc(),offline_observed=False,dashboard_return=False,source_launch_utc=r['launch_utc']);save(r,dest)
deadline=time.monotonic()+(1500 if a.kind=='windows' else 300)
while time.monotonic()<deadline:
    f=ftplib.FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=3);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        fresh_scan=False
        if a.kind=='scan' and not r['offline_observed']:
            # A very short helper can return before the first poll. Its unique
            # CREATE_NEW output still proves this specific scan completed.
            try:
                data=io.BytesIO();f.retrbinary('RETR /E/Applications/XWNSoak98b/snapshot.txt',data.write)
                fresh_scan=b'SNAPSHOT_COMPLETE success=1 ' in data.getvalue()
            except ftplib.error_perm:pass
        if r['offline_observed'] or fresh_scan:
            r['fresh_owned_snapshot_observed']=fresh_scan
            r.update(dashboard_return=True,returned_utc=utc());save(r,dest);print('Dashboard returned; collection/audits pending',flush=True);break
    except ftplib.all_errors:
        if not r['offline_observed']:r.update(offline_observed=True,offline_utc=utc());save(r,dest)
    finally:f.close()
    time.sleep(5)
else:r.update(timeout_utc=utc(),state='No dashboard return observed; screen state unknown');save(r,dest);print(r['state'],flush=True)
