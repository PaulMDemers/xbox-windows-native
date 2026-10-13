"""Verify retained evidence without requiring a failed experiment to pass."""
import datetime
import hashlib
import json
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
DEST = K / 'closeout002.json'
assert not DEST.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = {}
for case in ['control001', 'candidate001']:
    out = K / case
    run = Path('E:/xwn349/runs') / ('nt5-primary349-' + case)
    a = read(out / 'audit.json')
    q = read(out / 'log-protocol-qualification.json')
    closure = read(out / 'closure.json')
    assert closure['closed'] and closure['audit_sha256'] == sha(out / 'audit.json')
    assert closure['cleanup_sha256'] == sha(run / 'cleanup.json')
    assert q['original_audit_sha256'] == sha(out / 'audit.json')
    assert q['parser_sha256'] == sha(K / 'phase349_analysis.py')
    assert read(run / 'host-exit.json')['passed']
    for name, digest in read(out / 'emulator-frozen.json').items():
        assert sha(W / name) == digest, name
    fixture = read(out / 'fixture.json')
    assert sha(Path(fixture['fixture_path_windows'])) == fixture['fixture_sha256']
    captures = {p.relative_to(out / 'artifacts').as_posix(): sha(p)
                for p in (out / 'artifacts').rglob('*') if p.is_file()}
    actual = q['qualified_fields']
    assert actual['scoped_combined_passed'] == (case == 'control001')
    assert actual['strict_qualification_passed'] is False
    assert a['integrity_passed'] and a['normal_shutdown_count'] == 1
    assert a['orderly_host_exit']
    rows[case] = dict(
        closed=True, original_audit_sha256=sha(out / 'audit.json'),
        qualification_sha256=sha(out / 'log-protocol-qualification.json'),
        closure_sha256=sha(out / 'closure.json'),
        launch_sha256=sha(out / 'launch.json'),
        cleanup_sha256=sha(run / 'cleanup.json'),
        captures=captures, frozen_inputs=len(read(out / 'emulator-frozen.json')),
        actual_qualified_fields=actual,
        original_raw_parser_failure_preserved=not all(
            v['passed'] for v in a['large_phase_samples']))

build = read(K.parent / 'primary-copy348/build001.json')
for case in rows:
    assert sha(Path('E:/xwn348/build001') / case / 'xwnown.dll') == build['cases'][case]['sha256']
probe = read(K.parent / 'primary-copy348/probe/build001.json')
assert sha(Path(probe['output_windows'])) == probe['binary_sha256']
for name, digest in read(K / 'supplemental-protocol001.json')['pins'].items():
    assert sha(K / name) == digest, name
hosts = {}
for name in ['host001', 'host002']:
    result = read(K.parent / ('primary-copy348/' + name + '.json'))
    for filename, digest in result['files'].items():
        assert sha(Path('E:/xwn348') / name / filename) == digest, filename
    hosts[name] = len(result['files'])
diagnosis = read(K / 'coverage-diagnosis001.json')
assert diagnosis['qualified'] is False and diagnosis['hardware_promotion'] is False
assert diagnosis['observed_failure']['deficit_per_operation_bytes'] == 6036
assert read(K / 'pair-results.json')['scoped_matched_passed'] is False
assert not (K / 'final-review.json').exists()
result = dict(
    evidence_integrity_passed=True,
    experiment_qualified=False, hardware_promotion=False,
    checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    cases=rows, host_private_files_rehashed=hosts,
    driver_binaries_rehashed=True, probe_rehashed=True,
    diagnosis_sha256=sha(K / 'coverage-diagnosis001.json'),
    pair_results_sha256=sha(K / 'pair-results.json'),
    preserved_review_failure=dict(
        script='final-review.py', sha256=sha(K / 'final-review.py'),
        error="AssertionError ('candidate001', 0)",
        reason='Original closeout wrongly required all corrected samples to pass; it produced no output. The candidate coverage failure remains a failure.'),
    read_only_closeout=True, physical_access=False,
    all_original_event_gates_retained=True, performance_qualified=False)
DEST.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))
