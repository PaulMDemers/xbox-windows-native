"""Qualified functional counts, failed emulator event eligibility. No reruns."""
import json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'candidate001';read=lambda p:json.loads(p.read_text(encoding='utf-8'))
dest=k/'summary.json';assert not dest.exists()
fields=['source','event_id','type','strings','data_hex']
expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
events={}
for name in ['audit.json','physical-audit.json']:
    a=read(case/name);assert a['workload_passed']
    assert len(a['warnings_errors'])==len(expected)==1 and all(a['warnings_errors'][0][f]==expected[0][f] for f in fields)
    assert not a['new_events']['application']
    events[name]=[v for v in a['new_events']['system'] if v['source']=='Application Popup']
assert len(events['audit.json'])==1 and not events['physical-audit.json']
assert read(case/'audit.json')['integrity_passed']
assert read(case/'physical-audit.json')['preserved_files_exact'] and read(case/'physical-audit.json')['deployed_payloads_exact']
assert read(case/'physical-audit.json')['shared_acquire_success']
assert read(case/'physical-hive-audit.json')['passed'] and read(case/'restored-verification.json')['passed']
assert read(case/'closure.json')['closed'] and read(case/'physical-return.json')['closed']
for phase in ['emulator','physical']:assert read(k/(phase+'-counters.json'))['counter_coverage_passed']
assert not read(k/'eligibility-correction.json')['actual_emulator']['eligible']
p=read(case/'physical.json');assert p['baseline_restored'] and not p['startup_enabled']
physical=read(k/'physical-counters.json');lat=[n for op in physical['operations'] for v in op['samples'] for n in v['stats_latency_ms']]
r=dict(functional_counter_evidence_passed=True,scoped_counter_diagnostic_qualified=False,
    emulator_event_eligibility_passed=False,driver_changed=False,physical_original_restored_verified=True,
    physical_launch_utc=p['launch_utc'],physical_collect_utc=p['collected_utc'],physical_restore_utc=p['restored_utc'],
    emulator_checks=dict(samples=5,copies=20,loops=25,coherence=50),physical_checks=dict(samples=5,copies=20,loops=25,coherence=50),
    physical_stats_full_scan_ms=dict(min=min(lat),median=statistics.median(lat),max=max(lat)),
    readback_zero_upload_physical_samples=sum(v['uploads']==0 and v['bytes']==0 for v in physical['operations'][2]['samples']),
    emulator_shutdown_popup=events['audit.json'][0],physical_popups=[],
    inherited_strict_error=expected[0],strict_qualification_passed=False,release_qualified=False,
    failed_summary001_preserved='report-summary.py assertion caught type4 shutdown popup after physical collection; no output overwritten',
    procedural_failure='Physical review/ready screened warnings/application log but omitted system Application Popup; informational type4 slipped through. Future check-eligibility.py rejects all types. Executed packets preserved; no promotion or event waiver.',
    notes=['Device-global counters; all contaminated intervals retained','Identity112 geometry1024x576x32/60 stride4096 confirmed',
           'Full-screen check latency outside timed loops','No full physical allocation/all-file/storage or mode qualification',
           'No engine/upload split, optimized-driver or window-drag FPS claim'])
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['functional_counter_evidence_passed','scoped_counter_diagnostic_qualified','physical_stats_full_scan_ms','readback_zero_upload_physical_samples','emulator_shutdown_popup']},indent=2))
