"""Freeze NEW explicit interval experiment only after both194 runtime branches close."""
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from interval_policy import signature

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'physical-ready.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
capture = read(k / 'capture.json')
package = read(k / 'package-review.json')
tests = read(k / 'protocol-tests002.json')
policy_tests = read(k / 'interval-policy-tests.json')
assert capture['passed'] and package['passed'] and tests['passed'] and policy_tests['passed']
audit_tests = read(k / 'audit-boundary-tests.json')
assert audit_tests['passed'] and not audit_tests['physical_access']
assert audit_tests['production_ast_source_sha256'] == sha(k / 'audit-physical.py')
assert not tests['physical_access'] and not policy_tests['physical_access']
for test in [tests, policy_tests]:
    for name, expected in test['source_pins'].items():
        assert sha(k / name) == expected
helper = k.parent / 'video-measurement-boundary194'
build = read(helper / 'build-review.json')
assert build['passed'] and read(helper / 'boundary-parser-tests.json')['passed']
for case in ['idle001', 'pending001']:
    assert read(helper / case / 'closure.json')['closed']
    audit = read(helper / case / 'audit.json')
    assert audit['diagnostic_usable'] and audit['integrity_passed']
    assert audit['idle_branch_passed' if case == 'idle001' else 'pending_branch_passed']
for name, expected in read(helper / 'frozen-inputs.json').items():
    assert sha(ws / name) == expected
assert sha(k / 'artifacts/runner.exe') == package['helpers']['runner.exe'] == build['binary_sha256']
for name in ['runner.c', 'setup_gate.h', 'restart_gate.h', 'boundary_analysis.py']:
    assert (k / name).read_bytes() == (helper / name).read_bytes()
for name, provider in build['providers'].items():
    row = next(v for v in capture['files'] if v['path'] == '/F/winnt/system32/' + name)
    assert row['sha256'] == provider['sha256'] and row['second_read_exact']
assert read(k / 'binding-edit.json')['only_two_expected_values_changed']
assert sha(k / 'artifacts/gdi-probe.exe') == sha(k.parent / 'video-word-order186/artifacts/gdi-probe.exe')
assert next(v['sha256'] for v in capture['files'] if v['path'].endswith('/win32k.sys')) == read(k.parent / 'video-word-store184/driver-review.json')['provider_sha256']

baseline_paths = [k.parent / 'device-observation188/physical-audit.json',
                  k.parent / 'device-durability189/physical-audit.json',
                  k.parent / 'video-setup-physical193/control001/physical-audit.json']
documented = [signature(v) for v in read(baseline_paths[0])['warnings_errors']]
assert [(v['source'], v['event_id']) for v in documented] == [('Ftdisk', 49), ('Srv', 2013)]
assert all([signature(v) for v in read(p)['warnings_errors']] == documented for p in baseline_paths)
assert not (k.parent / 'video-setup-physical193/candidate001/physical.json').exists()
for case in ['control001', 'candidate001']:
    sys.argv = ['physical-controller.py', 'inspect', case]
    spec = importlib.util.spec_from_file_location('review_' + case, k / 'physical-controller.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    assert len(c.changes) == 3 and c.namespace == ('xwnpre195a' if case == 'control001' else 'xwnpre195b')
    assert not c.record.exists() and not c.art.exists()

sources = [p for p in k.iterdir() if p.suffix in ['.py', '.c', '.h']]
for p in sources:
    if p.suffix == '.py':
        ast.parse(p.read_text(encoding='utf-8'))
inputs = [k / name for name in ['creation.json', 'capture.json', 'package-review.json', 'binding-review.json',
          'binding-edit.json', 'protocol-tests002.json', 'interval-policy-tests.json', 'audit-boundary-tests.json', 'DESIGN.md',
          'artifacts/proposed-system', 'artifacts/runner.exe', 'artifacts/gdi-probe.exe']]
inputs += [k / 'artifacts' / row['path'].lstrip('/') for row in capture['files']]
inputs += baseline_paths + [helper / 'build-review.json', helper / 'frozen-inputs.json']
inputs += [helper / case / name for case in ['idle001', 'pending001'] for name in ['audit.json', 'closure.json']]
inputs += [ws / row['source'] for values in package['cases'].values() for row in values]
inputs += [ws / 'outputs' / name for name in ['fatx0098-soak3/physical.py', 'native-windows-physical-f/decode-legacy-events.py',
          'native-windows-nt5-kernel/nt5_hive_indexes.py', 'release-0.1.0/release.json']]
result = dict(prepared=True, physical_launch_performed=False, physical_qualified=False,
              release_qualified=False, strict_error_waiver=False,
              control_before_candidate=True, measurement_event_margin_seconds=1,
              documented_physical_warning_signatures=documented,
              scope='NEW explicit settled measurement comparison; all whole-boot warnings remain strict failures. '
                    'No override of193 gates, policy change or baseline promotion.',
              source_pins={p.name: sha(p) for p in sources},
              input_pins={p.relative_to(ws).as_posix(): sha(p) for p in inputs})
dest.write_text(json.dumps(result, indent=2) + '\n')
print('195 inputs/protocol/actual physical warning signatures frozen; no physical write/launch')
