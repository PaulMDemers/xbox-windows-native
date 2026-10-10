"""Close preserved host failure from existing cold captures; no launch/collection."""
import subprocess
from common import *
out=k/'control001';dest=out/'failure-closure.json';assert not dest.exists()
host=read(out/'host-state.json');trace=read(out/'trace.json');alloc=read(out/'allocation.json')
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/bootguard223-runs/nt5-bootguard223-control001')
assert host['closed'] and host['runner_exit']==1 and host['audit_exit']==1
assert not (out/'launch.json').exists() and not trace['events'] and not trace['guards']
assert trace['closed'] and trace['remaining_breakpoints'] and (run/'cleanup.json').exists()
for name,digest in read(k/'emulator-frozen.json').items():assert sha(ws/name)==digest,name
f=read(k/'fixture-control001.json');seed=Path(f['fixture_path_linux'])
assert sha(seed)==f['seed_sha256'] and sha(Path(f['parent']))==f['parent_sha256']
hives=[]
for name in HIVES:
    p=out/'artifacts'/('after-'+name);before=out/'artifacts'/('before-'+name)
    row=hive(p);assert sha(p)==sha(before)
    hives.append(dict(name=name,unchanged=True,**row))
for name in ['appevent.evt','sysevent.evt','setupapi.log']:
    assert sha(out/'artifacts'/('after-'+name))==sha(out/'artifacts'/('before-'+name))
assert alloc['allocation_consistent'] and not alloc['errors'] and not alloc['orphan_cluster_count']
result=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(seed),str(run/'hdd.qcow2')],capture_output=True,text=True)
save(dest,dict(closed=True,passed=False,physical_access=False,launches=0,recollections=0,
    host_failure='Tracer took monitor lock before runner NIC initialization; runner aborted and closed owned emulator.',
    audit_failure='Original auditor expected launch.json even though no launch was requested. Partial captures retained; never rerun original audit.',
    guard_writes=0,trace_breakpoints_at_transport_loss=trace['remaining_breakpoints'],
    teardown_qualified=False,process_closure_removes_instance=True,
    virtual_disk_equal=result.returncode==0,compare_exit=result.returncode,compare_output=result.stdout+result.stderr,
    hives=hives,allocation_passed=True,event_and_setupapi_bytes_unchanged=True,
    preserved_sha256={str(p.relative_to(ws)):sha(p) for p in [out/'host-state.json',out/'trace.json',out/'allocation.json',run/'cleanup.json'] if p.is_relative_to(ws)},
    cleanup_sha256=sha(run/'cleanup.json'),never_relaunch_or_recollect=True,
    limits='Closed failed host attempt, not guest/GPU/ordinary qualification; cold existing captures and additional whole-virtual-disk comparison only.'))
print(json.dumps(dict(closed=True,passed=False,virtual_disk_equal=result.returncode==0,guard_writes=0)))
