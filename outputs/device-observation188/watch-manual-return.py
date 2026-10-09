"""Separate188 observer after reported desktop and normal restart request; no relaunch."""
import os,time
from pathlib import Path
import physical as c
dest=c.k/'manual-return.json';assert not dest.exists()
previous=c.read(c.k/'physical-return.json');assert previous['closed'] and not previous['dashboard_return']
user=c.read(c.k/'user-observations.json');assert user['normal_restart_requested']
r=c.read(c.record);assert r['launch_requested'] and not r.get('collected_utc')
start=time.monotonic();data=dict(scope=__doc__,source_sha256=c.sha(Path(__file__).read_bytes()),observer_pid=os.getpid(),original_launch_utc=r['launch_utc'],new_launches=0,closed=False,dashboard_return=False,samples=[])
while time.monotonic()-start<300:
    sample=dict(utc=c.m.utc(),elapsed_since_observer_seconds=time.monotonic()-start,dashboard=False)
    try:
        with c.m.connect() as f:c.m.owner(f);sample.update(dashboard=True,reply=f.voidcmd('NOOP'))
    except Exception as exc:sample['error_type']=type(exc).__name__
    data['samples'].append(sample);data['dashboard_return']=sample['dashboard'];c.write_json(dest,data)
    if sample['dashboard']:break
    time.sleep(15)
data.update(closed=True,closed_utc=c.m.utc());c.write_json(dest,data)
print('Manual-return188 observer closed; dashboard_return='+str(data['dashboard_return'])+'; new_launches=0',flush=True)
