"""Closed matched functional/coverage result; emulator timing is not hardware."""
import hashlib,json,statistics
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'pair-results.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(K/'pair-input-review.json')['passed'];rows={};intervals=[]
for mode,case in enumerate(['control001','candidate001']):
 out=K/case;a=read(out/'audit.json');c=read(out/'closure.json');assert c['closed'] and c['audit_sha256']==sha(out/'audit.json')
 q=read(out/'log-protocol-qualification.json');assert q['original_audit_sha256']==sha(out/'audit.json')
 a.update(q['qualified_fields']);a['large_phase_samples']=q['corrected_phase_samples']
 rows[case]={n:a[n] for n in ['scoped_combined_passed','strict_qualification_passed','display_workload_passed','integrity_passed','orderly_host_exit','normal_shutdown_count','actual_caps','warnings_errors']}
 rows[case]['primary_coverage_passed']=all(v['passed'] for v in a['primary_samples'])
 rows[case]['audit_sha256']=sha(out/'audit.json')
 rows[case]['log_protocol_qualification_sha256']=sha(out/'log-protocol-qualification.json')
 for p,h in read(out/'emulator-frozen.json').items():assert sha(K.parents[1]/p)==h,p
 rows[case]['frozen_inputs_verified']=len(read(out/'emulator-frozen.json'))
 if not rows[case]['scoped_combined_passed']:continue
 assert len(a['primary_samples'])==len(a['large_phase_samples'])==5
 for id in [12,13]:
  primary=[v['intervals'][id] for v in a['primary_samples']];phase=[v['intervals'][id] for v in a['large_phase_samples']]
  assert all(v['passed'] and v['mode']==1 for v in a['large_phase_samples'])
  intervals.append(dict(case=case,id=id,fast_calls=sum(v['fast'] for v in primary),eligible_calls=sum(v['eligible'] for v in primary),fast_bytes=sum(v['fast_bytes'] for v in primary),wall_ms_per_operation_median=statistics.median(v['wall_ms']/v['operations'] for v in phase),selected_copy_body_ms_per_operation_median=statistics.median(v['elapsed_ms'][1]/v['operations'] for v in phase),upload_body_ms_per_operation_median=statistics.median(v['elapsed_ms'][2]/v['operations'] for v in phase)))
r=dict(scoped_matched_passed=all(v['scoped_combined_passed'] for v in rows.values()),strict_matched_passed=all(v['strict_qualification_passed'] for v in rows.values()),cases=rows,large_overlap_intervals=intervals,physical_access=False,hardware_performance_qualified=False,release_qualified=False,limits='Five samples in one boot per mode. Global counters include background work and preemption; selected CopyBits body differs from old Eng-only label. Body/wrapper overlap. Emulator timing cannot establish console speed. Original event gates unchanged.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
