"""Require full original storage workload, strict emulator events and cold consistency."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'004'
reports={};evidence={}
for name in ['audit','package-audit','allocation','collection','launch']:
    p=out/(name+'.json');reports[name]=json.loads(p.read_text());evidence[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
for stage in reports['collection']['stages'].values():
    assert hashlib.sha256((out/stage['output']).read_bytes()).hexdigest()==stage['sha256']
cleanup=ws/'work/runs/nt5-fatx-lock-order-soak-004/cleanup.json';assert cleanup.exists()
a=reports['audit'];v=reports['allocation'];w=a['workload']
gates=dict(audit=a['diagnostic_checks_passed'],setup=reports['package-audit']['null_setup_checks_passed'],
    workload=w['passed'] and w['mapping_checks']==527 and w['paint_api_replay_passed'],
    files=len(w['files'])==50 and all(f['matched'] for f in w['files']),
    absent=len(w['deleted_files_absent'])==34 and all(w['deleted_files_absent'].values()),
    duration=len(w['timed_rounds'])==15 and w['timed_rounds'][-1][1]>=900000 and w['required_duration_ms']==900000,
    shutdown=a['normal_shutdown_count']==1 and a['dashboard_return'],
    events=not a['unexpected_errors'] and not a['popup_records'] and not a['new_events']['application'],
    hives=len(a['hives'])==5 and all(h['parsed'] for h in a['hives']),
    allocation=v['allocation_consistent'] and not v['errors'] and not v['orphan_cluster_count'],
    ordinary=a['ordinary_run_valid'] and not (out/'timeout-memory.json').exists())
r=dict(scope=__doc__,passed=all(gates.values()),gates=gates,evidence_sha256=evidence,
    hardware_qualified=False,limits='Original mapping/BMP API workload, not actual Paint UI. Inherited emulator configuration and physical strict failures remain distinct; no new event gate waiver.')
p=out/'qualification.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
