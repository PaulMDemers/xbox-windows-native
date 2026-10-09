"""Separate read-only observer after user reported Windows desktop and was asked for normal restart."""
import datetime,importlib.util,json,sys,time
from pathlib import Path
base=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='control001';k=base/case
dest=k/'manual-return.json';assert not dest.exists()
sys.argv=['physical-controller.py','inspect',case]
spec=importlib.util.spec_from_file_location('controller',base/'physical-controller.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
assert c.read(k/'physical-return.json')['closed'] and not c.read(k/'physical-return.json')['dashboard_return']
r=c.read(c.record);assert r['launch_requested'] and not r.get('collected_utc')
start=time.time();samples=[];result=dict(scope=__doc__,user_observation='Windows2000 desktop',
    user_reported_crash=False,requested_action='Start/Shut Down/Restart; normal restart requested, not yet independently confirmed',
    new_launches=0,original_launch_utc=r['launch_utc'],observer_started_utc=c.m.utc(),closed=False,dashboard_return=False,samples=samples)
while time.time()-start<300:
    sample=dict(utc=c.m.utc(),elapsed_seconds=time.time()-start,dashboard=False)
    try:
        with c.m.connect() as f:c.m.owner(f);sample.update(dashboard=True,reply=f.voidcmd('NOOP'))
    except Exception as exc:sample['error_type']=type(exc).__name__
    samples.append(sample);result['dashboard_return']=sample['dashboard']
    tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest)
    if sample['dashboard']:break
    time.sleep(15)
result.update(closed=True,closed_utc=c.m.utc());dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(dashboard_return=result['dashboard_return'],samples=len(samples),new_launches=0)))
