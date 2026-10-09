"""Freeze NEW interval experiment after honest idle194 and ordinary pending197 supplement."""
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from interval_policy import signature
from prerequisite_policy import qualified_branches

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
dashboard = read(k / 'dashboard-preflight.json')
assert dashboard['passed'] and dashboard['writes'] == 0 and dashboard['launch_requested'] is False
assert dashboard['source_sha256'] == sha(k / 'dashboard-preflight.py')
assert dashboard['controller_sha256'] == sha(k / 'physical-controller.py')
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
observed = k.parent / 'video-boundary-boot196'
ordinary = k.parent / 'video-pending-ordinary197'
branches = [(helper, 'idle001'), (helper, 'pending001'), (observed, 'pending002'), (ordinary, 'pending001')]
audits = []
for folder, case in branches:
    closed = read(folder / case / 'closure.json')
    assert closed['closed'] and sha(folder / case / 'audit.json') == closed['audit_sha256']
    audits.append(read(folder / case / 'audit.json'))
assert qualified_branches(*audits)
prerequisite_tests = read(k / 'prerequisite-tests.json')
assert prerequisite_tests['passed'] and prerequisite_tests['actual197_evidence'] is False
for name, expected in prerequisite_tests['source_pins'].items():
    assert sha(k / name) == expected
parser_comparisons = []
reference_parser = (helper / 'boundary_analysis.py').read_bytes()
for folder in [observed, ordinary]:
    for name, expected in read(folder / 'frozen-inputs.json').items():
        assert sha(ws / name) == expected
    parser = (folder / 'boundary_analysis.py').read_bytes()
    # The197 authored copy adds only86 CRs at existing line endings; preserve raw pins.
    assert parser.replace(b'\r\n', b'\n') == reference_parser.replace(b'\r\n', b'\n')
    assert ast.dump(ast.parse(parser.decode('utf-8')), include_attributes=False) == ast.dump(ast.parse(reference_parser.decode('utf-8')), include_attributes=False)
    parser_comparisons.append(dict(folder=folder.name, raw_sha256=hashlib.sha256(parser).hexdigest(),
        reference_sha256=hashlib.sha256(reference_parser).hexdigest(), newline_only_difference=True, ast_identical=True))
of = read(ordinary / 'fixture-pending001.json')
assert of['fixture_sha256'] == read(observed / 'fixture-pending002.json')['fixture_sha256']
assert of['prerequisite196_closure_sha256'] == sha(observed / 'pending002/closure.json')
assert of['retained194_failure_sha256'] == sha(helper / 'pending001/closure.json')
assert of['protected']['F/xwnpre194/runner.exe'] == build['binary_sha256']
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
inputs += [folder / case / name for folder, case in branches[2:] for name in ['audit.json', 'closure.json']]
inputs += [folder / name for folder in [observed, ordinary] for name in ['frozen-inputs.json']]
inputs += [observed / 'fixture-pending002.json', ordinary / 'fixture-pending001.json', k / 'prerequisite-tests.json', k / 'dashboard-preflight.json']
inputs += [ws / row['source'] for values in package['cases'].values() for row in values]
inputs += [ws / 'outputs' / name for name in ['fatx0098-soak3/physical.py', 'native-windows-physical-f/decode-legacy-events.py',
          'native-windows-nt5-kernel/nt5_hive_indexes.py', 'release-0.1.0/release.json']]
result = dict(prepared=True, physical_launch_performed=False, physical_qualified=False,
              release_qualified=False, strict_error_waiver=False,
              control_before_candidate=True, measurement_event_margin_seconds=1,
              helper_prerequisites='194 idle plus NEW unobserved197 pending; failed194 retained,196 debugger observation separate',
              parser_comparisons=parser_comparisons,
              documented_physical_warning_signatures=documented,
              scope='NEW explicit settled measurement comparison; all whole-boot warnings remain strict failures. '
                    'No override of193 gates, policy change or baseline promotion.',
              source_pins={p.name: sha(p) for p in sources},
              input_pins={p.relative_to(ws).as_posix(): sha(p) for p in inputs})
dest.write_text(json.dumps(result, indent=2) + '\n')
print('195 inputs/protocol/actual physical warning signatures frozen; no physical write/launch')
