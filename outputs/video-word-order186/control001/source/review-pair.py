"""Independent closed-case comparison; no replay/collection and no event waiver."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'pair-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
for name in ['control001','candidate001']:
 out=k/name;c=read(out/'closure.json');a=read(out/'audit.json');package=read(out/'package-verification.json')
 assert c['closed'] and c['source_snapshot_exact']
 cases.append(dict(case=name,audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),workload_passed=a['workload_passed'],integrity_passed=a['integrity_passed'],strict_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],caps=a['actual_caps'],modes=a['actual_modes'],setupapi_unchanged=a['setupapi_unchanged'],package_bound=package['package_bound'],guard_lines=a['guard_lines'],normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],allocation=read(out/'allocation.json'),hives=len(a['hives']),protected_files=len(a['files']),live_copy_checks=20,additional_dib_checks=sum(6 for v in a['dib_samples'] if v['passed']),posttiming_checks=sum(v.get('posttiming_checks',0) for v in a['dib_samples']),timed_loops=sum(len(v['timed_loops']) for v in a['samples']),candidate_fast_rows=sum(v['fast_rows'] for s in a['dib_samples'] for v in s.get('intervals',[]))))
a,b=[read(k/name/'audit.json') for name in ['control001','candidate001']]
same=a['actual_caps']==b['actual_caps'] and a['actual_modes']==b['actual_modes']
rows=[]
for kind,label in enumerate(['fill','DIB_upload','readback','overlap_right_down','overlap_left_up']):
 values=[];counts=[]
 for audit in [a,b]:
  loops=[v['timed_loops'][kind] for v in audit['samples'] if v['loop_coverage']]
  values.append([v[3]/v[2] for v in loops]);counts.append([v[2] for v in loops])
 if len(values[0])==len(values[1])==5:
  c,d=[statistics.median(v) for v in values]
  rows.append(dict(kind=kind,label=label,control_ms_per_op=values[0],candidate_ms_per_op=values[1],control_counts=counts[0],candidate_counts=counts[1],control_median_ms_per_op=c,candidate_median_ms_per_op=d,control_over_candidate=c/d))
scoped=all(v['workload_passed'] and v['integrity_passed'] and v['package_bound'] and v['setupapi_unchanged'] for v in cases) and same
r=dict(scoped_display_and_cold_checks_passed=scoped,same_caps_modes=same,cases=cases,timings=rows,strict_qualification_passed=all(v['strict_passed'] for v in cases),physical_qualified=False,performance_qualified=False,release_qualified=False,
 limits='Two ordinary boots, candidate then control, five process samples each. Matched115 instrumentation and global background counters; coarse GetTickCount elapsed per operation, each loop>=1500ms. Emulator elapsed ratios are descriptive, not physical FPS or statistically isolated driver latency. Inherited null-device configuration explicit; no warning waiver.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(scoped_passed=scoped,strict_passed=r['strict_qualification_passed'],timings=rows),indent=2))
