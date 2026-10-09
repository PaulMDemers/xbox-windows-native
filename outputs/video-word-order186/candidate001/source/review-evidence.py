"""Independent final records review; no guest access, launch or collection."""
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'evidence-review.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
prior = read(k.parent / 'device-settled-reboot181/candidate001/audit.json')
fields = ['source', 'event_id', 'type', 'strings', 'data_hex']
assert len(prior['warnings_errors']) == 1
expected = {n: prior['warnings_errors'][0][n] for n in fields}
assert expected['source'] == 'Ftdisk' and expected['event_id'] == 49
pins = read(k / 'frozen-inputs.json')
for path, digest in pins.items():
    assert sha(ws / path) == digest, path

cases = []
for name in ['control001', 'candidate001']:
    out = k / name
    a = read(out / 'audit.json')
    c = read(out / 'closure.json')
    launch = read(out / 'launch.json')['cycles']
    assert c['closed'] and c['source_snapshot_exact']
    assert a['workload_passed'] and a['integrity_passed']
    assert not a['strict_qualification_passed']
    assert len(a['warnings_errors']) == 1
    assert {n: a['warnings_errors'][0][n] for n in fields} == expected
    assert not a['new_events']['application']
    assert a['event_history_preserved'] and a['setupapi_unchanged']
    assert a['guard_lines'] == ['INSTALL_WAIT_RESULT 0',
                               'INSTALL_FINAL_RESULT 0',
                               'NORMAL_RESTART_REQUEST 0']
    assert a['normal_shutdown_count'] == 1
    assert len(launch) == 1 and launch[0]['dashboard_return']
    assert all(v['passed'] and v['posttiming_checks'] == 3
               for v in a['dib_samples'])
    assert all(v['copy_checks_passed'] and v['loop_coverage']
               for v in a['samples'])
    package = read(out / 'package-verification.json')
    assert package['configuration_observed']
    assert all(not v['service'] and not v['function_driver_supported']
               for v in package['devices'])
    run = ws / 'work/runs' / ('nt5-word186-' + name)
    assert (run / 'cleanup.json').exists()
    caps = {int(v[1]): int(v[2]) for v in a['actual_caps']}
    geometry = [caps[8], caps[10], caps[12], caps[116]]
    assert geometry == [1024, 576, 32, 60]
    cases.append(dict(case=name, audit_sha256=sha(out / 'audit.json'),
                      closure_sha256=sha(out / 'closure.json'),
                      launch_requested_utc=launch[0]['launch_requested_utc'],
                      dashboard_return_utc=launch[0]['dashboard_return_utc'],
                      original_copy_checks=20, additional_dib_checks=30,
                      posttiming_checks=15, total_pixel_copy_checks=65,
                      timed_loops=25, scanout_comparisons=50,
                      actual_geometry=geometry,
                      strict_qualified=False, inherited_event_exact=True))
pair = read(k / 'pair-review.json')
assert pair['scoped_display_and_cold_checks_passed']
assert pair['same_caps_modes'] and not pair['strict_qualification_passed']
result = dict(passed=True, review_source_sha256=sha(Path(__file__)),
              frozen_pins_checked=len(pins), cases=cases,
              inherited_event=expected,
              ordinary_display_and_cold_scope_passed=True,
              strict_qualified=False, physical_access=False,
              hardware_performance_qualified=False,
              limits='Two reverse-order longer-interval emulator boots with five samples each. '
                     'Exact inherited event is retained as a strict failure; '
                     'no waiver, hardware promotion or release qualification.')
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
