"""Close the one-shot physical control from preserved evidence; no console access."""
import datetime
import hashlib
import json
import re
from pathlib import Path

base = Path(__file__).resolve().parent
workspace = base.parents[1]
case = base / 'control001'
dest = case / 'closure.json'
assert not dest.exists(), 'Never repeat closure'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
physical = read(case / 'physical.json')
audit = read(case / 'physical-audit.json')
hives = read(case / 'physical-hive-audit.json')
restored = read(case / 'restored-verification.json')
observer = read(case / 'physical-return.json')
ready = read(base / 'physical-ready.json')
assert physical['collected_utc'] and physical['baseline_restored']
assert not physical['startup_enabled'] and not physical.get('collection_failure')
assert observer['closed'] and restored['passed'] and hives['passed']
for name, expected in ready['source_pins'].items():
    assert digest(base / name) == expected, name
for name, expected in ready['input_pins'].items():
    assert digest(workspace / name) == expected, name
for group in ['before', 'after', 'before_payloads']:
    for row in physical[group].values():
        if row is not None:
            assert digest(workspace / row['path']) == row['sha256']

art = case / 'artifacts/physical'
before = (art / 'before-setupapi.log').read_bytes()
after = (art / 'after-setupapi.log').read_bytes()
prefix = after.startswith(before)
append = after[len(before):] if prefix else b''
text = append.decode('cp1252')
sections = []
for match in re.finditer(r'\[([^\]\r\n]+)\]([^\[]*)', text):
    body = match.group(2)
    commands = re.findall(r'Munged cmdline: ([^\r\n]+)', body)
    sections.append(dict(header=match.group(1), commands=commands,
                         no_compatible_driver='0xe0000228' in body))
setup = dict(before_bytes=len(before), after_bytes=len(after),
             history_exact_prefix=prefix, appended_bytes=len(append),
             appended_sha256=hashlib.sha256(append).hexdigest(),
             appended_non_ascii_bytes=sum(v >= 128 for v in append),
             sections=sections,
             limits='Log timestamps do not establish the untimestamped helper gate start. '
                    'This append does not resolve the older physical 111-byte corruption.')
assert audit['preserved_files_exact'] and audit['protected_files_exact']
assert audit['deployed_payloads_exact'] and audit['event_history_preserved']
assert audit['runner_log'].splitlines() == [
    'ATTEMPT_ONCE', 'WAITING_FOR_SETUP_IDLE', 'INSTALL_PREFLIGHT_RESULT 258',
    'MEASUREMENT_BLOCKED_SETUP_TIMEOUT 300000']
assert all(physical['after']['sample%d' % i] is None for i in range(5))
assert not audit['scoped_display_passed'] and not audit['event_signature_matches_inherited']
result = dict(
    closed=True, closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    physical_access=False, physical_result=True, case='control001',
    launch_count=1, collected_once=True, observer_closed=True,
    dashboard_return_during_observer=observer['dashboard_return'],
    later_dashboard_access_proved_by_collection=True,
    user_observation={'exact_reply': 'Yes I just restarted it',
                      'restart_ui_method_explicitly_confirmed': False},
    normal_shutdown_event_count=audit['normal_shutdown_count'],
    measured_samples=0, setup_pending_timeout_ms=300000,
    restored_verification_passed=restored['passed'], hive_audit_passed=hives['passed'],
    startup_enabled=False, baseline_restored=True, source_input_pins_exact=True,
    strict_qualification_passed=False, scoped_display_passed=False,
    candidate_launch_permitted=False, candidate_ever_launched=False,
    warnings_errors=[{'source': v['source'], 'event_id': v['event_id'],
                     'strings': v['strings']} for v in audit['warnings_errors']],
    setupapi=setup,
    source_sha256=digest(Path(__file__)),
    evidence_pins={p.name: digest(p) for p in [
        case / 'physical.json', case / 'physical-return.json', case / 'physical-audit.json',
        case / 'physical-hive-audit.json', case / 'restored-verification.json']},
    owned_processes_running=[],
    limits='Safe refusal and exact rollback, not a graphics comparison, clean-event '
           'qualification, full physical allocation/file audit or setup-policy fix.')
dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'closed': True, 'samples': 0, 'baseline_restored': True,
                  'setupapi_append_bytes': len(append), 'candidate_permitted': False}))
