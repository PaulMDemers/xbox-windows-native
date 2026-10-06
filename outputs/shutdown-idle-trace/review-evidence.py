"""Cross-check the preserved minimal trace against independent cold evidence."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
out = k / '001'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
trace = read(out / 'trace.json')
early = read(out / 'trace-early.json')
audit = read(out / 'audit.json')
package = read(out / 'package-audit.json')
allocation = read(out / 'allocation.json')
runtime = read(out / 'runtime.json')
fixture = read(k / 'fixture-001.json')
ordinary = read(k.parent / 'shutdown-install-idle/002/audit.json')
source_fixture = read(k.parent / 'shutdown-install-idle/fixture-002.json')
caller = read(k.parent / 'shutdown-popup-workload/caller-review.json')
launch = read(out / 'launch.json')
run = ws / 'work/runs/nt5-shutdown-idle-trace-001'
cleanup = read(run / 'cleanup.json')

assert trace['trace_source_sha256'] == sha(out / 'trace-source.py')
assert early['trace_source_sha256'] == sha(out / 'trace-early-source.py')
assert early['status'] == 'capture_incomplete' and early['events'] == []
assert early['error'] == "AssertionError('E14')" and early['guest_resumed']
assert 'readable_kernel_site_bytes_verified' not in early
assert trace['status'] == 'reached_kernel_shutdown' and trace['guest_resumed']
assert trace['all_kernel_sites_readable_initially']
assert trace['readable_kernel_site_bytes_verified']
assert not trace.get('unreadable_site_hits') and not trace.get('error')
assert sha(k / 'site-review.json') == sha(k.parent / 'shutdown-popup-workload/site-review.json')
for name in ['fixture_sha256', 'seed_sha256', 'payloads', 'fatx_sha256']:
    assert fixture[name] == source_fixture[name]
assert len(launch['cycles']) == 1 and launch['cycles'][0]['dashboard_return']

events = trace['events']
assert [e['function'] for e in events] == [
    '_ExRaiseHardError@24', '_ExpRaiseHardError@24', '_NtShutdownSystem@4']
a, b, shutdown = events
assert a['owner'] == b['owner'] and a['thread'] == b['thread']
assert a['arguments'][0] == b['arguments'][0] == '0xc000026b'
assert a['owner']['command_line'].startswith('rundll32.exe newdev.dll,DevInstall PCI\\VEN_1B36&DEV_0005&')
assert a['caller'] == caller['caller']
assert next(m for m in runtime['modules'] if m['name'] == 'win32k.sys') == caller['runtime_module']
assert shutdown['owner']['image'] == 'winlogon.exe' and shutdown['arguments'] == ['0x1']
assert a['tick_count'] == b['tick_count'] < shutdown['tick_count']
for e in events:
    assert not any(name.endswith('decode_error') for name in e)
    assert 'decode_error' not in e['owner']
assert len(audit['popup_records']) == len(ordinary['popup_records']) == 1
for name in ['source', 'event_id', 'type', 'strings', 'data_hex']:
    assert audit['popup_records'][0][name] == ordinary['popup_records'][0][name]
assert audit['idle_completed'] and audit['idle_elapsed_ms'] == 120000
assert audit['storage_workload_not_run'] and audit['normal_shutdown_count'] == 1
assert audit['dashboard_return'] and not audit['unexpected_errors']
assert not audit['new_events']['application']
assert all(v['matched'] for v in audit['payloads'] + audit['runtime_binary_checks'])
assert all(audit['baseline_checks'].values()) and audit['fatx_exact']
assert len(audit['hives']) == 5 and all(h['parsed'] for h in audit['hives'])
assert package['installation_checks_passed'] and not package['combined_checks_passed']
assert allocation['capture_complete'] and allocation['allocation_consistent']
assert allocation['orphan_cluster_count'] == 0 and not allocation['errors']
assert not audit['ordinary_run_valid'] and not audit['diagnostic_checks_passed']

report = dict(
    scope=__doc__, evidence_consistent=True, physical_access=False,
    ordinary_run_valid=False, popup_fixed=False, strict_result='FAIL: shutdown popup',
    source_hashes={p.name: sha(p) for p in [out/'trace-source.py', out/'trace-early-source.py']},
    fixture_sha256=fixture['fixture_sha256'], seed_sha256=fixture['seed_sha256'],
    runtime_kernel_base=runtime['kernel_base'], runtime_win32k=caller['runtime_module'],
    first_attachment=dict(status=early['status'], error=early['error'], events=0,
                          guest_resumed=early['guest_resumed'],
                          limit='Failed during pre-arm reading; unreadable site was not recorded.'),
    second_attachment=dict(status=trace['status'], events=len(events),
                           all_kernel_sites_readable_initially=True,
                           guest_resumed=trace['guest_resumed']),
    error_owner=a['owner'], error_thread=a['thread'], status=a['arguments'][0],
    caller=a['caller'], error_tick=a['tick_count'], kernel_shutdown_tick=shutdown['tick_count'],
    popup_matches_ordinary_idle_failure=True, idle_ms=audit['idle_elapsed_ms'],
    installation_checks_passed=True, checked_payloads=len(audit['payloads']),
    checked_runtime_binaries=len(audit['runtime_binary_checks']), structural_hives=5,
    allocation={n: allocation[n] for n in ['directories','files','directory_clusters','orphan_cluster_count','allocation_consistent']},
    launch=launch['cycles'][0], cleanup=cleanup,
    limits=[
        'Two hard-error entries observe one error, not two popups.',
        'No creation, resume, token closure or termination boundary was traced.',
        'The following win32k termination request is matched static evidence only.',
        'Paused runtime capture and breakpoint stops may alter scheduling.',
        'No explicit mapping/BMP workload; ordinary Windows background I/O remains.',
        'Full F: allocation scan and selected binary hashes, not all partitions or a full archive audit.',
        'Do not assign this emulator device to the physical console popup.',
    ])
(k / 'evidence-review.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({n: report[n] for n in ['evidence_consistent','strict_result','ordinary_run_valid','popup_fixed']}))
