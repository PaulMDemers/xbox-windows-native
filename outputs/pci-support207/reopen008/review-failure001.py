"""Preserve the failed host observer separately from the cold guest checks."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(k/'preflight001.json');r=read(case/'run.json');t=read(case/'trace.json');a=read(case/'audit.json');n=read(case/'pnp-review.json')
for name,digest in p['sources'].items():assert sha(k/name)==digest
for path,digest in p['dependencies'].items():assert sha(Path(path))==digest
assert r['closed'] and r['source_unchanged'] and not r.get('failure')
assert t['status']=='capture_incomplete' and t['error']=='''NameError("name 'call' is not defined")'''
assert t['guest_resumed'] and t['breakpoints_remaining']==0 and t['pending_call_count']==0 and not t['calls']
assert t['hit_counts']=={'open_enter':1} and not t.get('cleanup_error')
assert a['integrity_passed'] and all(n[x] for x in ('qualified_resource_only_installation','hal_probe_passed','lifecycle_completed','cancel_remove_qualified'))
result=dict(review_passed=True,caller_trace_usable=False,failure=t['error'],failure_kind='host observer dispatch indentation',closed_utc=r['closed_utc'],source_unchanged=True,guest_resumed=True,breakpoints_remaining=0,cold_integrity_passed=True,normal_shutdown=False,physical_access=False,script_sha256=sha(Path(__file__)),evidence_sha256={p.name:sha(p) for p in case.glob('*.json')},limits='No caller or functional-input inference from this observer. Existing HID conflict evidence remains in hidreject007. Never relaunch this used fixture.')
dest=k/'failure-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print('Failed observer preserved; cleanup and cold resource/integrity gates verified')
