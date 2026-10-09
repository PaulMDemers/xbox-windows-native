"""One post-closure review; a guarded hold is not a qualified reboot."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';dest=out/'guard-verification.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(out/'audit.json');c=read(out/'closure.json');b=read(k/'build-review.json');f=read(k/'frozen-inputs.json')
assert c['closed'] and not c['debugger'] and not c['physical_access']
for name,digest in f.items():assert sha(ws/name)==digest,name
for p in (out/'source').iterdir():assert p.read_bytes()==(k/p.name).read_bytes()
assert b['sha256']==sha(k/'artifacts/runner.exe') and b['source_sha256']==sha(k/'runner.c')
assert b['host_tests']['header_sha256']==b['header_sha256']==sha(k/'restart_gate.h')
assert b['host_tests']['passed'] and b['host_tests']['asan_ubsan'] and b['host_tests']['cases']==8
assert not a['debugger'] and a['display_workload_passed'] and a['integrity_passed']
assert a['guard_observation_passed']
assert a['runner_guard_blocked'] or a['runner_normal_restart']
assert all(v['matched'] for v in a['files']) and len(a['hives'])==5
alloc=read(out/'allocation.json');assert alloc['capture_complete'] and alloc['allocation_consistent'] and not alloc['errors'] and alloc['orphan_cluster_count']==0
if a['runner_guard_blocked']:
    assert not a['runner_normal_restart'] and not a['dashboard_return'] and a['normal_shutdown_count']==0
    assert not a['workload_passed'] and not a['strict_qualification_passed']
    assert not any(x.startswith('NORMAL_RESTART_REQUEST') for x in a['guard_lines'])
launch=read(out/'launch.json');assert len(launch['cycles'])==1
inventory=read(out/'device-inventory.json')
unbound=[]
for phase in inventory['hives']:
    for d in phase['devices']:
        if not d['values'].get('Driver') and not d['values'].get('Service'):
            unbound.append(dict(phase=phase['phase'],path=d['path']))
r=dict(passed=True,debugger=False,physical_access=False,
    guard_blocked=a['runner_guard_blocked'],guard_lines=a['guard_lines'],display_workload_passed=a['display_workload_passed'],
    integrity_passed=a['integrity_passed'],normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
    strict_qualification_passed=a['strict_qualification_passed'],unbound_devices=unbound,
    frozen_pins=len(f),source_snapshot_exact=True,hashes={p.name:sha(p) for p in [Path(__file__),out/'audit.json',out/'closure.json',out/'device-inventory.json',k/'build-review.json']},
    limits='Held guard run and host-bound stop are distinct from a successful reboot or soak. No popup absence promoted to a fix; two idle queries cannot atomically exclude future installation. Physical baseline unchanged. Legacy frozen emulator-ready.scope wording is inaccurate; actual Run/launch/audit flags establish ordinary new-runner execution.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['passed','guard_blocked','guard_lines','display_workload_passed','integrity_passed','normal_shutdown_count','strict_qualification_passed']}))
