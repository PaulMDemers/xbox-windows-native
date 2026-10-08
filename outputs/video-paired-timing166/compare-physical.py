"""Summarize the two completed five-sample physical trials without promoting release."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'paired-physical.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
names=['opaque fill','DIB to screen','screen to DIB','overlap right/down','overlap left/up']
cases={}
fields=['source','event_id','type','strings','data_hex']
expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
for case in ['control001','candidate001']:
    a=read(k/case/'physical-audit.json');h=read(k/case/'physical-hive-audit.json');r=read(k/case/'restored-verification.json')
    same=len(a['warnings_errors'])==len(expected)==1 and all(a['warnings_errors'][0][f]==expected[0][f] for f in fields)
    assert a['workload_passed'] and a['preserved_files_exact'] and a['event_history_preserved'] and h['passed'] and r['passed']
    assert same and not a['new_events']['application'] and not any(v['source']=='Application Popup' for v in a['new_events']['system'])
    assert a['actual_caps']==read(k/'control001/physical-audit.json')['actual_caps']
    if case=='candidate001':assert a['shared_acquire_success'] and a['deployed_payloads_exact']
    series={kind:[] for kind in range(5)}
    for sample in a['samples']:
        for row in sample['timed_loops']:
            kind,count,ms=map(int,row[1:]);assert count==2000 or ms>=1500
            series[kind].append(dict(count=count,milliseconds=ms,ms_per_operation=ms/count))
    assert all(len(v)==5 for v in series.values())
    cases[case]=dict(samples=5,live_checks=20,timed_loops=25,series=series,
        workload_passed=a['workload_passed'],hives_passed=h['passed'],baseline_restored=r['passed'],
        strict_qualification_passed=False,same_baseline_error_signature=same,
        helper_sha256=read(k/'build-review.json')['sha256'],probe_sha256=read(k/'build-review.json')['probe_sha256'])
ops=[]
for kind,name in enumerate(names):
    b=[v['ms_per_operation'] for v in cases['control001']['series'][kind]]
    c=[v['ms_per_operation'] for v in cases['candidate001']['series'][kind]]
    ops.append(dict(kind=kind,operation=name,baseline_median_ms=statistics.median(b),candidate_median_ms=statistics.median(c),
        baseline_range_ms=[min(b),max(b)],candidate_range_ms=[min(c),max(c)],
        median_rate_ratio=statistics.median(b)/statistics.median(c)))
result=dict(scoped_paired_timing_passed=True,physical_result=True,cases=cases,operations=ops,
    strict_release_qualified=False,full_storage_qualified=False,window_drag_fps_qualified=False,
    limitations='Two boots, baseline first, same operation order; five within-boot samples each. Small256x128 synchronous GDI work includes flush/message/visibility costs. No all-file or allocation audit on physical disk. Ft49 is retained, not waived.',
    original_display_and_system_restored=True,additional_launches_issued=0)
dest.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
print(json.dumps(ops,indent=2))
