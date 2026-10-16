"""One explicit user-authorized retry after reported dashboard-only launch."""
import time
from physical import *

ticket()
for p,h in read(K/'source-pins.json').items():assert sha((W/p).read_bytes())==h,p
first=read(K/'launch.json');assert first['launch_requested']
stage=read(K/'stage002.json');assert stage['completed']
dest=K/'launch002.json';assert not dest.exists()
observation=K/'launch001-user-observation.json';assert not observation.exists()
write_json(observation,dict(recorded_utc=utc(),user_report="It never booted into windows, I saw the dashboard screensaver vanish but that's it. Retry",windows_boot_observed=False,retry_explicitly_authorized=True,original_launch_record_preserved=True))
out=PRIVATE/'retry002-before';assert not out.exists();out.mkdir()
r=dict(utc=utc(),launch_requested=False,user_authorized_retry=True,previous_launch='launch.json',
       physical_writes=False,drivers_unchanged=True,normal_startup_unchanged=True,
       console_C_accessed=False,verified_files={},events={},command=first['command'])
write_json(dest,r)
with connect() as f:
    for p,h in installed().items():
        data=get(f,p);assert sha(data)==h,p;r['verified_files'][p]=sha(data)
    for p,v in stage['verified'].items():
        data=get(f,p);assert sha(data)==v['sha256'],p;r['verified_files'][p]=sha(data)
    before=read(K/'before.json')
    for name in ['sysevent.evt','appevent.evt']:
        p='/E/winnt/system32/config/'+name;data=get(f,p);(out/name).write_bytes(data)
        r['events'][name]=dict(bytes=len(data),sha256=sha(data),unchanged_since_initial_preflight=sha(data)==before['files'][p]['sha256'])
    r.update(launch_requested=True,launch_utc=utc());write_json(dest,r);f.sock.settimeout(20)
    try:r['reply']=f.sendcmd(r['command'])
    except Exception as exc:r['reply_uncertain']=type(exc).__name__
    write_json(dest,r)
print('One user-authorized retry sent; no console files changed',flush=True)
samples=[]
for i in range(6):
    time.sleep(5);row=dict(utc=utc(),dashboard=False)
    try:
        with connect(timeout=3):row['dashboard']=True
    except Exception as exc:row['error']=type(exc).__name__
    samples.append(row);write_json(K/'retry002-reachability.json',dict(samples=samples,windows_boot_not_proven=True))
    if not row['dashboard']:break
print('Dashboard reachable after retry:',samples[-1]['dashboard'],flush=True)
