"""Independent observed-trial closure, including fresh post-scan baseline readback."""
from common001 import *
out=k/'physical001';dest=k/'final-review.json';assert not dest.exists();pins()
trial=read(out/'trial.json');collection=read(out/'collection.json');audit=read(out/'audit.json');scan=read(out/'scan.json');allocation=read(out/'allocation.json')
assert trial['launch_requested'] and trial['baseline_restored'] and not trial['startup_enabled']
assert collection['completed'] and collection['startup_restored'] and collection['baseline_restored'] and all(collection['restored_payloads'].values())
assert scan['collected'] and scan['snapshot_complete'] and read(out/'scan-return.json')['dashboard_return']
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
with connect(timeout=8) as f:
 fixed_after=check_fixed(f)
 restored={v['path']:get(f,v['path'])==incoming(v['path']) for v in read(k/'package.json')['video']}
 assert all(restored.values()) and get(f,startup)==incoming(startup)
mutable=['system','software','sam','security','default','sysevent.evt','appevent.evt']
unchanged={n:(k/'artifacts/before001/F/winnt/system32/config'/n).read_bytes()==(k/'artifacts/physical001/F/winnt/system32/config'/n).read_bytes() for n in mutable}
for name in ['setupapi.log','system32/xwn-video-trace.bin']:
 unchanged[name]=(k/'artifacts/before001/F/winnt'/name).read_bytes()==(k/'artifacts/physical001/F/winnt'/name).read_bytes()
missing=[p for p,v in collection['files'].items() if p.startswith('/F/xwnhd315/') and v is None]
private={str(p.relative_to(k)):sha(p.read_bytes()) for p in (k/'artifacts/physical001').rglob('*') if p.is_file()}
save(out/'private-artifacts.json',private)
save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,normal_startup_restored=True,baseline_restored=True,audit_sha256=sha((out/'audit.json').read_bytes()),source_sha256=sha(pathlib.Path(__file__).read_bytes())))
r=dict(closed_utc=utc(),physical_access=True,launch_utc=trial['launch_utc'],return_observation=read(out/'return.json'),fixed_after=fixed_after,restored_payloads=restored,unchanged=unchanged,missing_logs=missing,new_events=audit['new_events'],normal_shutdown_count=audit['normal_shutdown_count'],allocation={n:allocation[n] for n in ['directories','files','directory_clusters','orphan_cluster_count','errors']},integrity_passed=audit['integrity_passed'],scoped_passed=audit['scoped_combined_passed'],strict_passed=audit['strict_qualification_passed'],physical720p_qualified=audit['scoped_combined_passed'],physical1080i_qualified=False,release_qualified=False,private_capture_count=len(private),frozen_files=len(read(k/'frozen.json')),limits='Observed retry; screen reports are separate user evidence. No inferred crash/failed-register attribution. shared_acquire_success is historical if the video trace is unchanged. Original physical baseline restored/readback after scan; allocation audit is not a whole-disk content comparison.')
save(dest,r);print(json.dumps({n:r[n] for n in ['unchanged','normal_shutdown_count','allocation','integrity_passed','scoped_passed','strict_passed']},indent=2))
