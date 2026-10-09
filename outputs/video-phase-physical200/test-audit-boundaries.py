"""Replay actual200 checkpoint/event AST against closed194 bytes; host-only adversaries."""
import ast
import hashlib
import json
from pathlib import Path
from boundary_analysis import analyze as boundary_analyze
from interval_policy import measurement_events

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'audit-boundary-tests.json'
assert not dest.exists()
source = k / 'audit-physical.py'
text = source.read_text(encoding='utf-8')
start = text.index('checkpoint_rows=')
end = text.index('result.update(samples=', start)
code = compile(ast.parse(text[start:end]), str(source), 'exec')
prior = k.parent / 'video-measurement-boundary194/idle001'
actual = json.loads((prior / 'audit.json').read_text())
attempt = actual['logs']['attempt.log']
root = k / 'artifacts/audit-boundary-tests'
root.mkdir(exist_ok=False)
snapshot = (prior / 'artifacts/setup-after.log').read_bytes()
altered = root / 'altered-snapshot'
altered.write_bytes(b'X' + snapshot[1:])
rows = {name: {'path': (prior / 'artifacts' / name).relative_to(ws).as_posix()}
        for name in ['setup-before.log', 'setup-after.log']}
checks = []

def run(label, events, pair=None, history=None, expected=True):
    art = root / label
    art.mkdir()
    for name in ['before-setupapi.log', 'after-setupapi.log']:
        data = (prior / 'artifacts' / name).read_bytes()
        if history and name == 'after-setupapi.log':
            data = history
        (art / name).write_bytes(data)
    env = dict(r={'after': rows if pair is None else pair}, ws=ws, art=art,
               attempt=attempt, result={'new_events': events},
               boundary_analyze=boundary_analyze, measurement_events=measurement_events)
    exec(code, env)
    result = env['result']
    accepted = all(result[n] for n in ['setup_gate_passed', 'setupapi_history_preserved',
                                     'checkpoint_history_preserved', 'measurement_events_passed'])
    assert accepted == expected, label
    checks.append(dict(name=label, expected=expected, actual=accepted))

run('actual194_bytes_and_events', actual['new_events'])
interval, _ = measurement_events(attempt, [])
warning = dict(actual['warnings_errors'][0], generated_unix=interval[0])
run('warning_during_measurement', {'system': [warning], 'application': []}, expected=False)
warning = dict(warning, generated_unix=interval[1] + 1)
run('warning_at_margin', {'system': [warning], 'application': []}, expected=False)
warning = dict(warning, generated_unix=interval[1] + 2)
run('warning_outside_interval_remains_separate', {'system': [warning], 'application': []})
run('missing_snapshot', actual['new_events'], dict(rows, **{'setup-after.log': None}), expected=False)
run('same_size_changed_snapshot', actual['new_events'],
    dict(rows, **{'setup-after.log': {'path': altered.relative_to(ws).as_posix()}}), expected=False)
run('damaged_boot_history', actual['new_events'], history=b'X' + snapshot[1:], expected=False)
run('truncated_boot_history', actual['new_events'], history=snapshot[:-1], expected=False)
dest.write_text(json.dumps(dict(passed=True, physical_access=False, real_launches=0,
    actual_closed194_snapshots_and_event_delta=True, production_ast_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    checks=checks, limits='Host replay of actual production block, not physical results or qualification.'), indent=2) + '\n')
print('200 production checkpoint/history/event block passed eight actual-byte/adversarial replays')
