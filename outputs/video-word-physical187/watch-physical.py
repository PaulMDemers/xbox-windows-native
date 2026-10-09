"""Observe a single recorded launch; never launch or modify console state."""
import datetime
import importlib.util
import json
import time,sys
from pathlib import Path

base=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case
spec = importlib.util.spec_from_file_location('controller', base / 'physical-controller.py')
c = importlib.util.module_from_spec(spec)
sys.argv=['physical-controller.py','inspect',case];spec.loader.exec_module(c)
dest = k / 'physical-return.json'
assert not dest.exists()
r = c.read(c.record)
assert r['launch_requested'] and not r.get('collected_utc')
launch = datetime.datetime.fromisoformat(r['launch_utc']).timestamp()
deadline = launch + 420
samples = []
while time.time() < deadline:
    now = time.time()
    sample = dict(utc=c.m.utc(), elapsed_seconds=now-launch, dashboard=False)
    if now-launch >= 45:
        try:
            with c.m.connect() as f:
                c.m.owner(f)
                sample['dashboard'] = True
                sample['reply'] = f.voidcmd('NOOP')
        except Exception as exc:
            sample['error_type'] = type(exc).__name__
    samples.append(sample)
    data = dict(scope=__doc__, launch_utc=r['launch_utc'], samples=samples,
                dashboard_return=sample['dashboard'], closed=False)
    tmp = dest.with_suffix('.tmp')
    tmp.write_bytes((json.dumps(data, indent=2)+'\n').encode('utf-8'))
    tmp.replace(dest)
    if sample['dashboard']:
        break
    time.sleep(15)
data.update(closed=True, closed_utc=c.m.utc())
dest.write_bytes((json.dumps(data, indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(dashboard_return=data['dashboard_return'], samples=len(samples))))
