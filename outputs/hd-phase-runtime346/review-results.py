"""Summarize closed matched phase runs; no hardware or performance promotion."""
import hashlib,json,statistics
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'pair-results.json';assert not dest.exists()
assert read(K/'pair-input-review.json')['passed']
rows={};pins={};groups={}
for mode,case in enumerate(['control001','candidate001']):
    out=K/case;a=read(out/'audit.json');c=read(out/'closure.json')
    assert c['closed'] and c['audit_sha256']==sha(out/'audit.json')
    rows[case]={n:a[n] for n in ['scoped_combined_passed','strict_qualification_passed','display_workload_passed','integrity_passed','orderly_host_exit','normal_shutdown_count','actual_caps','actual_modes','warnings_errors']}
    pins[case]=dict(audit_sha256=sha(out/'audit.json'),fixture_sha256=read(out/'fixture.json')['fixture_sha256'])
    if not a['scoped_combined_passed']:continue
    assert len(a['large_phase_samples'])==5
    for sample in a['large_phase_samples']:
        assert sample['passed'] and sample['mode']==mode and len(sample['intervals'])==15
        for v in sample['intervals']:
            key=(v['id'],v['kind'],tuple(v['size']))
            groups.setdefault(key,{}).setdefault(case,[]).append(v)
complete=all(v['scoped_combined_passed'] for v in rows.values())
summary=[]
if complete:
    assert len(groups)==15 and rows['control001']['actual_caps']==rows['candidate001']['actual_caps'] and rows['control001']['actual_modes']==rows['candidate001']['actual_modes']
    for (ident,kind,size),pair in sorted(groups.items()):
        row=dict(id=ident,kind=kind,size=size,cases={})
        for case,values in pair.items():
            assert len(values)==5
            wall=[v['wall_ms']/v['operations'] for v in values]
            row['cases'][case]=dict(samples=5,operations=[v['operations'] for v in values],wall_ms_per_operation_median=statistics.median(wall),wall_ms_per_operation_range=[min(wall),max(wall)],phase_ms_per_operation_medians=[statistics.median(v['elapsed_ms'][i]/v['operations'] for v in values) for i in range(4)])
        summary.append(row)
r=dict(scoped_matched_clock_coverage_passed=complete,strict_matched_qualification_passed=all(v['strict_qualification_passed'] for v in rows.values()),physical_qualified=False,performance_qualified=False,cases=rows,pins=pins,intervals=summary,limits='Five samples within one launch per mode, not independent repeated boots. Timing is emulator diagnostic data. Counters are device-global, include preemption/background and have overlapping engine/body/wrapper categories; never sum them. OFF/ON changes profiling overhead, not rendering algorithms. No hardware speedup, FPS, deployment or release qualification; all strict warnings remain failures.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['scoped_matched_clock_coverage_passed','strict_matched_qualification_passed','physical_qualified','performance_qualified']}))
