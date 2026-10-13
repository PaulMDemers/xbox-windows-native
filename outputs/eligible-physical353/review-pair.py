"""Physical diagnostic attribution with original event failures preserved."""
import hashlib,json,statistics
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'pair-results.json';assert not dest.exists();cases={};intervals={}
for mode,case in enumerate(['control001','candidate001']):
    out=K/case;a=read(out/'audit.json');c=read(out/'collection.json');assert c['completed'] and c['startup_restored'] and c['driver_restored']
    cases[case]={n:a[n] for n in ['diagnostic_workload_completed','scoped_combined_passed','strict_qualification_passed','display_workload_passed','integrity_passed','normal_shutdown_count','actual_caps','actual_modes','warnings_errors','interval_warning_errors']}
    cases[case]['audit_sha256']=sha(out/'audit.json')
    if not a['display_workload_passed']:continue
    assert len(a['large_phase_samples'])==5
    for sample in a['large_phase_samples']:
        assert sample['passed'] and sample['mode']==1 and len(sample['intervals'])==15
        for v in sample['intervals']:intervals.setdefault((v['id'],v['kind'],tuple(v['size'])),{}).setdefault(case,[]).append(v)
complete=all(v['diagnostic_workload_completed'] for v in cases.values());summary=[]
if complete:
    assert len(intervals)==15 and cases['control001']['actual_caps']==cases['candidate001']['actual_caps'] and cases['control001']['actual_modes']==cases['candidate001']['actual_modes']
    for (ident,kind,size),pair in sorted(intervals.items()):
        row=dict(id=ident,kind=kind,size=size,cases={})
        for case,values in pair.items():
            assert len(values)==5;wall=[v['wall_ms']/v['operations'] for v in values]
            row['cases'][case]=dict(operations=[v['operations'] for v in values],wall_ms_per_operation_median=statistics.median(wall),wall_ms_per_operation_range=[min(wall),max(wall)],phase_ms_per_operation_medians=[statistics.median(v['elapsed_ms'][i]/v['operations'] for v in values) for i in range(4)])
        summary.append(row)
r=dict(diagnostic_pair_completed=complete,scoped_combined_passed=all(v['scoped_combined_passed'] for v in cases.values()),strict_qualification_passed=all(v['strict_qualification_passed'] for v in cases.values()),performance_qualified=False,release_qualified=False,cases=cases,intervals=summary,phase_labels=['EngBitBlt','selected_CopyBits_body','upload_copy_body','complete_upload_wrapper'],limits='Physical sequential boots with five samples each. Global elapsed counters include background/preemption; wrapper contains copy-body and profiler overhead. Do not sum overlapping categories or infer FPS/speedup. Event failures remain failures; diagnostic completion only permits reporting these observations. Original startup/driver restored each case, Xbox C outside tools, F system retained.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['diagnostic_pair_completed','scoped_combined_passed','strict_qualification_passed','performance_qualified']}))
