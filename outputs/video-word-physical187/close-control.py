"""Close preserved held control after startup-first collection/restored baseline; candidate remains blocked."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=k/'control001';dest=case/'closure.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(case/'physical.json');a=read(case/'physical-audit.json');h=read(case/'physical-hive-audit.json');v=read(case/'restored-verification.json')
assert r.get('collected_utc') and r['baseline_restored'] and not r['startup_enabled'] and v['passed'] and h['passed']
assert a['probe_passed'] and a['pixel_checks_passed'] and a['counters_passed'] and a['loop_coverage']
assert not a['scoped_display_passed'] and not a['normal_restart_requested'] and not a['event_signature_matches_inherited']
assert 'INSTALL_WAIT_RESULT 258' in a['runner_log'] and 'RESTART_BLOCKED_PENDING_INSTALL 258' in a['runner_log']
assert read(case/'manual-return.json')['dashboard_return'] and read(case/'manual-return.json')['closed']
assert not (k/'candidate001/physical.json').exists()
packet=read(k/'physical-ready.json')
assert all(sha(k/name)==digest for name,digest in packet['source_pins'].items())
assert all(sha(ws/name)==digest for name,digest in packet['input_pins'].items())
dep=read(k/'dependency002-review.json');assert all(sha(ws/v['path'])==v['sha256'] for v in dep['dependencies'])
series={kind:[] for kind in range(5)}
for sample in a['samples']:
    for _,kind,count,ms in sample['timed_loops']:series[kind].append(dict(operations=count,milliseconds=ms,ms_per_operation=ms/count))
result=dict(scope=__doc__,closed=True,physical_result=True,ordinary_qualified=False,strict_qualified=False,
    user_observation='Windows2000 desktop after observer deadline; normal restart requested through Start/Shut Down/Restart',
    manual_restart_method_independently_captured=False,late_dashboard_return=True,original_automatic_return=False,
    launch_utc=r['launch_utc'],collected_utc=r['collected_utc'],restored_utc=r['restored_utc'],
    pixel_copy_checks=65,timed_loops=25,scanout_comparisons=50,probe_exit_zero_count=5,
    guard_status=258,guard_refused_restart=True,normal_eventlog_shutdown_count=a['normal_shutdown_count'],
    protected_hashes_exact=a['protected_files_exact'],payloads_exact=a['deployed_payloads_exact'],
    shared_acquisition_passed=a['shared_acquire_success'],hive_snapshots_valid=10,selected_device_service_policy_unchanged=True,
    event_history_preserved=a['event_history_preserved'],warnings_errors=a['warnings_errors'],
    application_popups=[v for v in a['new_events']['system'] if v['source']=='Application Popup'],
    setupapi_unchanged=False,setupapi_delta_sha256=sha(case/'pending-inventory.json'),
    baseline_restored_readback=True,normal_startup_restored=True,candidate_never_launched=True,
    timing_series=series,off_medians_ms={kind:statistics.median(v['ms_per_operation'] for v in rows) for kind,rows in series.items()},
    no_hardware_improvement_comparison=True,frozen_preparation_pins_unchanged=True,local_running_sessions=[],
    evidence_pins={p.relative_to(k).as_posix():sha(p) for p in [case/n for n in ['physical.json','physical-return.json','waiting-manual.json',
        'manual-return.json','physical-audit.json','physical-hive-audit.json','restored-verification.json','pending-inventory.json']]},
    next='Identify/complete actual pending device setup with explicit live ownership evidence before preparing any new physical comparison. No repeats of187 or gate waiver.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('Held control closed with65 checks but guard258/popups/Srv strict failure; baseline restored; ON never launched')
