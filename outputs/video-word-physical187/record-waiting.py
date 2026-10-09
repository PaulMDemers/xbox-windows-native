"""Record bounded observer timeout without inferring crash, qualifying trial or repeating launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001']
dest=k/case/'waiting-manual.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/case/'physical.json');observer=read(k/case/'physical-return.json')
assert r['launch_requested'] and not r.get('collected_utc') and observer['closed'] and not observer['dashboard_return']
packet=read(k/'physical-ready.json');ws=k.parents[1]
assert all(sha(k/name)==digest for name,digest in packet['source_pins'].items())
assert all(sha(ws/name)==digest for name,digest in packet['input_pins'].items())
dep=read(k/'dependency002-review.json');assert all(sha(ws/v['path'])==v['sha256'] for v in dep['dependencies'])
result=dict(scope=__doc__,physical_result=True,trial_closed=False,host_observer_closed=True,
    launch_utc=r['launch_utc'],observer_closed_utc=observer['closed_utc'],
    startup_enabled=r['startup_enabled'],baseline_restored=r['baseline_restored'],
    workload_outcome='Unknown: no workload/event results collected',crash_inferred=False,
    qualified=False,manual_input_required='Actual console screen state; ask once',
    launch_record_sha256=sha(k/case/'physical.json'),observer_sha256=sha(k/case/'physical-return.json'),
    preparation_pins_unchanged=True,dependencies_unchanged=True,local_running_sessions=[],
    next='Never relaunch. On dashboard return collect once startup-first, restore original display/SYSTEM, verify readback and audit retained evidence.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('Observer closed; physical trial unresolved and preserved; no crash inferred or relaunch')
