"""Summarize completed emulator setup/workload gates without changing historical results."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case in ['003','004']
def read(path):return json.loads(path.read_text())
evidence={};cases={}
for c in ['001','002',case]:
    reports={}
    for name in ['audit','package-audit','allocation','collection','launch']:
        p=k/c/(name+'.json');reports[name]=read(p)
        evidence[str(p.relative_to(k))]=hashlib.sha256(p.read_bytes()).hexdigest()
    cleanup=ws/('work/runs/nt5-shutdown-null-placeholder-'+c+'/cleanup.json')
    assert cleanup.exists()
    for stage in reports['collection']['stages'].values():
        assert hashlib.sha256((k/c/stage['output']).read_bytes()).hexdigest()==stage['sha256']
    a=reports['audit'];p=reports['package-audit'];v=reports['allocation']
    cases[c]=dict(passed=all([a['diagnostic_checks_passed'],p['null_setup_checks_passed'],
        v['allocation_consistent'],not v['errors'],not v['orphan_cluster_count'],
        a['normal_shutdown_count']==1,a['dashboard_return'],not a['popup_records'],
        not a['unexpected_errors'],len(a['hives'])==5,all(h['parsed'] for h in a['hives'])]),
        ordinary=a['ordinary_run_valid'],normal_shutdown=a['normal_shutdown_count']==1 and a['dashboard_return'],cleanup=read(cleanup))
work=read(k/case/'audit.json')['workload'];duration=900000 if case=='004' else 60000
workload_pass=all([work['passed'],work['mapping_checks']==527,len(work['files'])==50,
    all(v['matched'] for v in work['files']),len(work['deleted_files_absent'])==34,
    all(work['deleted_files_absent'].values()),work['paint_api_replay_passed'],
    len(work['timed_rounds'])==15,work['timed_rounds'][-1][1]>=duration,
    work['required_duration_ms']==duration,cases[case]['ordinary']])
r=dict(scope=__doc__,emulator_configuration_passed=all(v['passed'] for v in cases.values()) and workload_pass,
    case=case,cases=cases,workload_passed=workload_pass,mapping_checks=work['mapping_checks'],
    bmp_api_cases=16,exact_files=len(work['files']),absent_files=len(work['deleted_files_absent']),
    duration_ms=work['timed_rounds'][-1][1],evidence_sha256=evidence,
    hardware_qualified=False,original_shutdown_race_fixed=False,
    limits='Parent retains previous01B0/01B4 FAILEDINSTALL flags. Supported GPU setup and emulator-only unused-function null INF; no function driver or physical qualification. Earlier shutdown stall remains unresolved; no new event gate waiver. Actual Paint UI not tested here.')
target=k/case/'qualification.json';assert not target.exists();target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['case','emulator_configuration_passed','mapping_checks','duration_ms','hardware_qualified']},indent=2))
