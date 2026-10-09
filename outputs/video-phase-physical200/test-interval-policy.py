"""Actual closed194 timing/physical193 warnings plus conservative interval adversaries."""
import hashlib
import json
from pathlib import Path
from interval_policy import signature, documented_only, measurement_events, candidate_permitted

k = Path(__file__).resolve().parent
dest = k / 'interval-policy-tests.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
physical = read(k.parent / 'video-setup-physical193/control001/physical-audit.json')
warnings = physical['warnings_errors']
known = [signature(v) for v in warnings]
assert len(known) == 2 and documented_only(warnings, known)
assert documented_only([], known) and documented_only(warnings[:1], known)
assert not documented_only(warnings + warnings[:1], known)
assert not documented_only([dict(warnings[0], event_id=999)], known)
log = (k.parent / 'video-measurement-boundary194/idle001/artifacts/attempt.log').read_text()
interval, _ = measurement_events(log, [])
start, end = interval
outside = [dict(warnings[0], generated_unix=start - 2), dict(warnings[1], generated_unix=end + 2)]
assert measurement_events(log, outside)[1] == []
inside = [dict(warnings[0], generated_unix=start - 1), dict(warnings[1], generated_unix=end + 1)]
assert measurement_events(log, inside)[1] == inside
assert measurement_events(log, [dict(warnings[0], generated_unix=start)])[1]
for bad in [log + '\nMEASUREMENT_START_TIME 0 0',
            log.replace('MEASUREMENT_END_TIME', 'MISSING_END_TIME'),
            'MEASUREMENT_START_TIME 0 0\nMEASUREMENT_END_TIME 0 0']:
    try:
        measurement_events(bad, [])
        raise RuntimeError('Bad clock accepted')
    except (AssertionError, ValueError):
        pass
assert not candidate_permitted(physical, {'passed': True}, {'passed': True})
good = dict(scoped_display_passed=True, warnings_are_documented_baseline_only=True)
assert candidate_permitted(good, {'passed': True}, {'passed': True})
for a, h, r in [(dict(good, scoped_display_passed=False), {'passed': True}, {'passed': True}),
                (dict(good, warnings_are_documented_baseline_only=False), {'passed': True}, {'passed': True}),
                (good, {'passed': False}, {'passed': True}),
                (good, {'passed': True}, {'passed': False})]:
    assert not candidate_permitted(a, h, r)
result = dict(passed=True, physical_access=False, real_launches=0,
              actual194_timestamps_used=True, actual193_failure_refused=True,
              strict_warning_failure_retained=True, conservative_margin_seconds=1,
              tests=['known/absent/duplicate/unknown signature', 'interval inside/margin/outside',
                     'missing/duplicate/pre-epoch clock', 'failed control/hives/rollback refusal'],
              source_pins={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [Path(__file__), k / 'interval_policy.py']})
dest.write_text(json.dumps(result, indent=2) + '\n')
print('Actual194 interval and193 failure verified; unknown/duplicate/in-interval warnings block comparison')
