"""Compare two closed hardware text-copy scopes; never deploy or infer FPS."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = root / 'physical-pair-review.json'
assert not dest.exists(), 'Never overwrite a completed comparison'
cases = {}
pins = {}
for name in ['control001', 'candidate001']:
    out = root / name
    a = read(out / 'physical-audit.json')
    c = read(out / 'closure.json')
    assert c['closed'] and c['scoped_display_passed'] and c['baseline_restored']
    assert not c['startup_enabled']
    for filename, digest in c['evidence_pins'].items():
        assert sha(out / filename) == digest
    assert a['physical_result'] and a['scoped_display_passed'] and a['workload_passed']
    assert a['text_coverage_passed'] and a['measurement_events_passed']
    assert a['warnings_are_documented_baseline_only'] and not a['strict_error_waiver']
    assert read(out / 'physical-hive-audit.json')['passed']
    assert read(out / 'restored-verification.json')['passed']
    assert a['normal_shutdown_count'] == 1 and a['dashboard_return']
    assert a['boundary_analysis']['helper']['targets'] == [1, 2, 3, 4]
    assert len(a['text_samples']) == 5
    assert all(v['passed'] and len(v['cases']) == 13 for v in a['text_samples'])
    assert all(v['moves'] == 40 and v['exact_readbacks'] == 40 for v in a['window_samples'])
    assert [(v['source'], v['event_id']) for v in a['warnings_errors']] == [('Ftdisk', 49)]
    assert not a['strict_events_passed'] and not a['strict_qualification_passed']
    cases[name] = a
    pins[name] = dict(audit_sha256=sha(out / 'physical-audit.json'), closure_sha256=sha(out / 'closure.json'))

control, candidate = cases['control001'], cases['candidate001']
assert control['actual_caps'] == candidate['actual_caps']
assert control['actual_modes'] == candidate['actual_modes']
rows = []
for index in range(13):
    left = [v['cases'][index] for v in control['text_samples']]
    right = [v['cases'][index] for v in candidate['text_samples']]
    # Require equal visible coverage, font dispatch and client geometry. The
    # actual input clips are retained separately: the optimization intentionally
    # changes the copy intersection, not the supplied clip or rendered pixels.
    for field in ['changed_pixels', 'guard_pixels', 'calls', 'glyphs', 'client', 'origin', 'bounds', 'input_clip', 'clip_complexity']:
        assert all(v[field] == left[0][field] for v in left + right), (index, field)
    x = [v['copied_bytes'] for v in left]
    y = [v['copied_bytes'] for v in right]
    assert len(set(x)) == len(set(y)) == 1 and y[0] <= x[0]
    rows.append(dict(case=index, control_bytes=x[0], candidate_bytes=y[0],
                     reduction_percent=None if not x[0] else 100 * (x[0] - y[0]) / x[0],
                     matched_changed_pixels=left[0]['changed_pixels'], calls=left[0]['calls']))

result = dict(passed=True, physical_result=True,
              optimization_demonstrated=any(v['candidate_bytes'] < v['control_bytes'] for v in rows),
              rows=rows, cases=pins, baseline_restored=True, startup_enabled=False,
              strict_events_passed=False, strict_qualification_passed=False,
              full_storage_qualified=False, release_qualified=False,
              source_sha256=sha(Path(__file__)),
              limits='Five samples of matched actual text pixels, input clips and copied bytes on physical Xbox. Reduction is redundant text upload only; preceding background drawing remains. No whole-operation speed, desktop FPS, new video mode, storage/dump or release qualification. Inherited pre-measurement Ftdisk49 remains a strict failure.')
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
