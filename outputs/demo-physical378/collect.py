"""Post-demo read-only collection; retained demo startup is an intended change.
The original physical.py collect compared startup to the old baseline; do not use it.
"""
import importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('demo',K/'physical.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
dest=m.O/'collection.json';assert not dest.exists()
assert m.read(m.O/'launch.json')['requested']
r=dict(utc=m.utc(),files={},console_C_accessed=False,read_only=True)
with m.connect() as f:
    for n in ['outline-first.txt','outline-applied.txt']:
        b=m.fetch(f,m.NS+'/'+n,True);r['files'][n]=None if b is None else dict(sha256=m.sha(b),text=b.decode('ascii'))
    for p,h in m.fixed.items():
        if p!=m.START:assert m.sha(m.fetch(f,p))==h,p
    assert m.sha(m.fetch(f,m.START))==m.read(K.parent/'demo-settings376/package001.json')['startup']['sha256']
    for p,v in m.policy.items():assert m.sha(m.fetch(f,p))==v['sha256'],p
    user=m.fetch(f,'/E/documents and settings/win2k/ntuser.dat')
    assert m.fetch(f,'/E/documents and settings/win2k/ntuser.dat')==user
    q=m.A/'after-ntuser.dat';assert not q.exists();q.write_bytes(user)
    r.update(drivers_and_F_rollback_unchanged=True,demo_startup_retained=True,ntuser_sha256=m.sha(user),
             outline_log_passed=bool(r['files']['outline-first.txt']) and 'PASS: current-user setting and saved profile agree.' in r['files']['outline-first.txt']['text'])
m.write_json(dest,r);print(json.dumps(r,indent=2))
