"""Observe the single201 physical boot for five minutes; no relaunch or writes to Xbox."""
import os, sys, time
from pathlib import Path
import controller as c
sys.path.insert(0, str(c.kit.parent / 'gpu-reset-banner152'))
from ftp_deadline import DeadlineFTP

dest = c.k / 'return.json'
assert not dest.exists()
r = c.read(c.record)
assert r['launch_requested'] and not r.get('collected_utc')
data = dict(scope=__doc__, observer_pid=os.getpid(), launch_utc=r['launch_utc'],
            closed=False, dashboard_return=False, offline_observed=False, samples=[], new_launches=0)
deadline = time.monotonic() + 300
while time.monotonic() < deadline:
    sample = dict(utc=c.m.utc(), dashboard=False)
    f = DeadlineFTP(min(deadline, time.monotonic() + 7))
    try:
        f.connect(os.environ['XWN_FTP_HOST'], timeout=f.budget())
        f.login(os.environ['XWN_FTP_USER'], os.environ['XWN_FTP_PASSWORD'])
        c.m.owner(f)
        sample['dashboard'] = True
    except Exception as exc:
        sample['error_type'] = type(exc).__name__
        data['offline_observed'] = True
    finally:
        f.close()
    data['samples'].append(sample)
    data['dashboard_return'] = sample['dashboard'] and data['offline_observed']
    c.write_json(dest, data)
    if data['dashboard_return']:
        break
    time.sleep(min(10, max(0, deadline-time.monotonic())))
data.update(closed=True, closed_utc=c.m.utc())
c.write_json(dest, data)
print('201 physical observer closed: dashboard_return=' + str(data['dashboard_return']), flush=True)
