"""Two physical OFF/ON boots; retain strict errors and report raw five-sample timing distributions."""
import json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'paired-physical.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());cases={}
for case in ['control001','candidate001']:
    a=read(k/case/'physical-audit.json');h=read(k/case/'physical-hive-audit.json');v=read(k/case/'restored-verification.json');p=read(k/case/'physical.json')
    assert a['scoped_display_passed'] and a['event_signature_matches_inherited'] and h['passed'] and v['passed']
    assert a['actual_caps']==read(k/'control001/physical-audit.json')['actual_caps'] and a['actual_modes']==read(k/'control001/physical-audit.json')['actual_modes']
    series={kind:[] for kind in range(5)}
    for sample in a['samples']:
        for _,kind,count,ms in sample['timed_loops']:
            assert count<=20000 and ms>=1500
            series[kind].append(dict(count=count,milliseconds=ms,ms_per_operation=ms/count))
    assert all(len(v)==5 for v in series.values())
    cases[case]=dict(launch_utc=p['launch_utc'],return_utc=read(k/case/'physical-return.json')['closed_utc'],
        series=series,samples=5,pixel_copy_checks=65,timed_loops=25,scanout_comparisons=50,
        workload_passed=True,hives_passed=True,baseline_restored=True,strict_events_passed=a['strict_events_passed'],
        strict_qualification_passed=False,warnings_errors=a['warnings_errors'],global_row_intervals=[v['intervals'] for v in a['row_samples']])
ops=[]
for kind,name in enumerate(['opaque fill','DIB to screen','screen to DIB','overlap right/down','overlap left/up']):
    old=[v['ms_per_operation'] for v in cases['control001']['series'][kind]]
    new=[v['ms_per_operation'] for v in cases['candidate001']['series'][kind]]
    b,c=statistics.median(old),statistics.median(new)
    ops.append(dict(kind=kind,operation=name,off_median_ms=b,on_median_ms=c,off_range_ms=[min(old),max(old)],
        on_range_ms=[min(new),max(new)],median_elapsed_reduction_percent=100*(1-c/b),median_rate_ratio=b/c))
result=dict(scope=__doc__,scoped_paired_timing_passed=True,physical_result=True,cases=cases,operations=ops,
    actual_caps=read(k/'control001/physical-audit.json')['actual_caps'],actual_modes=read(k/'control001/physical-audit.json')['actual_modes'],
    strict_release_qualified=False,full_storage_qualified=False,window_drag_fps_qualified=False,new_modes_qualified=False,
    original_display_and_system_restored=True,additional_launches=0,
    limitations='Two boots OFF first; five within-boot samples and same operation order.256x128 synchronous GDI includes flush/message/visibility costs and global background accounting. No physical allocation/all-file audit or release promotion. Ft49 retained as strict failure.')
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(ops,indent=2))
