"""Compare decoded cold EVT records; do not attribute historical errors to this boot."""
import json
from pathlib import Path

k = Path(__file__).resolve().parent
read = lambda name: json.loads((k / name).read_text())
audit = read('emulator-audit.json')
result = {'scope': 'Bounded GDI run; scanned legacy records, not a full storage audit', 'logs': {}}
for name in ['system', 'application']:
    before = read('before-'+name+'-events.json')['records']
    after = read(name+'-events.json')['records']
    assert len({r['record'] for r in before}) == len(before)
    assert len({r['record'] for r in after}) == len(after)
    indexed = {r['record']: r for r in after}
    assert all(indexed.get(r['record']) == r for r in before), 'Prior records changed or rotated'
    limit = max((r['record'] for r in before), default=0)
    added = [r for r in after if r['record'] > limit]
    result['logs'][name] = dict(before_last_record=limit, new_records=added)
new = result['logs']['system']['new_records']
assert [(r['source'], r['event_id']) for r in new] == [
    ('Service Control Manager', 7000), ('EventLog', 6009), ('EventLog', 6005),
    ('Ftdisk', 49), ('EventLog', 6006)]
assert new[0]['strings'] == ['HID Input Service', '%%2']
assert new[3]['strings'] == ['\\Device\\HarddiskVolume6']
assert not result['logs']['application']['new_records']
assert audit['passed'] and audit['runner_normal_restart_requested']
assert read('launch.json')['dashboard_return']
result.update(passed=True, eventlog_normal_stop_record=new[-1]['record'],
              caveats=['Existing HID service failure and Ftdisk 49 recur; they are not resolved by this probe',
                       'No new delayed-write event or application event in this bounded run',
                       'Emulator timings include concurrent host build activity and are not physical performance'])
(k/'event-review.json').write_text(json.dumps(result, indent=2)+'\n')
audit.update(event_review_pending=False, event_review='event-review.json',
             normal_restart_observed=True, emulator_closed=True,
             qualification='PASS bounded GDI correctness and cold log persistence; not a driver change',
             timing_caveat=result['caveats'][-1])
(k/'emulator-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
print(json.dumps(dict(passed=True, normal_stop_record=new[-1]['record'])))
