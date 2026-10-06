"""Qualify one completed concurrency diagnostic; a timeout never passes."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case=='001';out=k/case
read=lambda p:json.loads(p.read_text())
reports={};evidence={}
for name in ['audit','allocation','collection','launch']:
    p=out/(name+'.json');reports[name]=read(p)
    evidence[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
for stage in reports['collection']['stages'].values():
    assert hashlib.sha256((out/stage['output']).read_bytes()).hexdigest()==stage['sha256']
cleanup=ws/('work/runs/nt5-fatx-cleanup-order-'+case+'/cleanup.json')
assert cleanup.exists()
a=reports['audit'];v=reports['allocation'];l=reports['launch']
gates=dict(workload=a['workload_completed'],worker_files=len(a['worker_files'])==2 and all(f['exact'] for f in a['worker_files']),
    audit=a['diagnostic_checks_passed'],normal_shutdown=a['normal_shutdown_count']==1,
    return_observed=len(l['cycles'])==1 and l['cycles'][0].get('dashboard_return') is True,
    no_new_event_failures=not a['unexpected_errors'] and not a['popup_records'] and not a['new_events']['application'],
    five_structural_hives=len(a['hives'])==5 and all(h['parsed'] for h in a['hives']),
    allocation=v['allocation_consistent'] and not v['errors'] and not v['orphan_cluster_count'],
    ordinary_before_deadline=a['ordinary_run_valid'] and not a['debugger_observation_before_deadline'],
    no_timeout_capture=not a['post_deadline_snapshot'])
r=dict(scope=__doc__,case=case,passed=all(gates.values()),gates=gates,evidence_sha256=evidence,
    elapsed_ms=a['elapsed_ms'],cleanup=read(cleanup),hardware_qualified=False,
    limits='A bounded concurrency pass cannot prove all lock orderings correct. A cold allocation pass after timeout does not qualify workload completion or normal shutdown. Physical baseline and earlier failures are unchanged.')
p=out/'qualification.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
