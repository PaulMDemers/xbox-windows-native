"""Preserve one post-timeout snapshot from this owned experiment; never alter guest data."""
import datetime,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001'];out=k/case
run=ws/('work/runs/nt5-fatx-namespace-stress-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
launch=json.loads((out/'launch.json').read_text())
assert launch['cycles'][0].get('dashboard_return') is False,'Only after recorded return timeout'
report=out/'timeout-memory.json';raw=out/'artifacts/timeout.ram'
assert not report.exists() and not raw.exists();raw.parent.mkdir(exist_ok=True)
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
r=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,paused=True,guest_writes=False)
lock=acquire_monitor_lock(4594);running=False
try:
    r['status_before']=command(4594,'info status');running='VM status: running' in r['status_before']
    command(4594,'stop');r['registers']=command(4594,'info registers')
    command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()))
    data=raw.read_bytes();assert len(data)==67108864
    r.update(captured=True,raw_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
except Exception as e:r.update(captured=False,error=repr(e))
finally:
    try:
        if running:r['resume_reply']=command(4594,'cont')
    finally:
        lock.close();report.write_text(json.dumps(r,indent=2)+'\n')
print({n:r[n] for n in ['captured','error'] if n in r})
