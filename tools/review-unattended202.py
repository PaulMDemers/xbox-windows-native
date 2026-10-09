"""Read-only review of preserved202 raw packets, closures and frozen inputs."""
import hashlib
import json
import sys
from pathlib import Path

ws = Path(__file__).resolve().parents[1]
k = ws / 'outputs/video-unattended202'
sys.path.insert(0, str(k))
from runner_analysis import analyze

read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
kind = sys.argv[1]
assert kind in ['emulator', 'control001', 'candidate001']
cases = ['control001', 'candidate001'] if kind == 'emulator' else [kind]
dest = k / ('raw-review-' + kind + '.json')
assert not dest.exists()
records = []
pins = {}
for case in cases:
    physical = kind != 'emulator'
    out = k / (case if physical else 'emu-' + case)
    art = out / 'artifacts' / 'physical' if physical else out / 'artifacts'
    a = read(out / ('physical-audit.json' if physical else 'audit.json'))
    closure = read(out / 'closure.json')
    assert closure['closed'] and closure['scoped_display_passed']
    assert a['scoped_display_passed'] and a['normal_shutdown_count'] == 1
    assert a['dashboard_return'] and a['measurement_events_passed']
    assert not a['strict_events_passed'] and not a['strict_qualification_passed']
    prefix = 'after-' if physical else ''
    attempt = (art / (prefix + 'attempt.log')).read_bytes()
    wizard = (art / (prefix + 'wizard201.log')).read_bytes()
    snapshots = [(art / (prefix + n)).read_bytes() for n in ['setup-before.log', 'setup-after.log']]
    b = analyze(attempt.decode('ascii'), snapshots, wizard, int(not physical))
    assert b['idle_branch_passed'] and b['cancellation_passed']
    assert b['helper']['targets'] == ([1, 2, 3, 4] if physical else [1, 2, 5])
    assert snapshots[0] == snapshots[1]
    text = attempt.decode('ascii').splitlines()
    assert text.count('ATTEMPT_ONCE') == 1
    assert [v for v in text if v.startswith('SAMPLE_EXIT_ZERO ')] == ['SAMPLE_EXIT_ZERO ' + str(i) for i in range(5)]
    assert text[-3:] == ['INSTALL_WAIT_RESULT 0', 'INSTALL_FINAL_RESULT 0', 'NORMAL_RESTART_REQUEST 0']
    packets = [art / ('after-sample%d' % i if physical else 'sample%d/gdi-baseline.txt' % i) for i in range(5)]
    for p in packets:
        raw = p.read_bytes()
        assert raw.endswith(b'PASS 0 0 0\r\n') and b'FAIL' not in raw and b'\0' not in raw
    assert all(v['moves'] == v['exact_readbacks'] == 40 for v in a['window_samples'])
    if physical:
        assert read(out / 'restored-verification.json')['passed']
        assert read(out / 'physical-hive-audit.json')['passed']
        state = read(out / 'physical.json')
        assert state['baseline_restored'] and not state['startup_enabled']
        assert a['warnings_are_documented_baseline_only']
        for name, digest in closure['evidence_pins'].items():
            assert sha(out / name) == digest
    else:
        assert a['integrity_passed'] and a['allocation_passed']
        assert [(v['source'], v['event_id']) for v in a['warnings_errors']] == [('Ftdisk', 49)]
        assert sha(out / 'audit.json') == closure['audit_sha256']
    paths = packets + [art / (prefix + n) for n in ['attempt.log', 'wizard201.log', 'setup-before.log', 'setup-after.log']]
    paths += list(out.glob('*.json'))
    pins.update({p.relative_to(ws).as_posix(): sha(p) for p in paths})
    records.append(dict(case=case,physical=physical,actions=b['helper']['actions'],targets=b['helper']['targets'],helper_exit=0,samples=5,window_readbacks=200,setup_bytes=len(snapshots[0]),normal_shutdown=True,baseline_restored=physical,strict_qualified=False))
frozen = read(k / ('physical-ready.json' if kind != 'emulator' else 'emulator-frozen.json'))
groups = [frozen] if kind == 'emulator' else [{('outputs/video-unattended202/' + n): s for n,s in frozen['source_pins'].items()}, frozen['input_pins']]
for group in groups:
    for name, digest in group.items():
        assert sha(ws / name) == digest, name
result = dict(passed=True,physical_access=False,review_source_sha256=sha(Path(__file__)),kind=kind,cases=records,evidence_pins=pins,strict_qualified=False,limits='Raw packet and existing cold/typed/closure review only; inherited warnings are strict failures, no full physical storage, performance or release qualification.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,indent=2))
