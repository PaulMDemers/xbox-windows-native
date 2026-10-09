"""Parser adversaries around exact captured191 lifecycle and actual193 refusal."""
import hashlib
import json
from pathlib import Path
from boundary_analysis import analyze, GUIDANCE

k = Path(__file__).resolve().parent
dest = k / 'boundary-parser-tests.json'
assert not dest.exists()
old = (k.parent / 'video-setup-runtime191/idle001/artifacts/attempt.log').read_text().splitlines()
snapshot = (k.parent / 'video-setup-runtime191/idle001/artifacts/before-setupapi.log').read_bytes()
at = old.index('MEASUREMENT_BEGIN')
def checkpoint(t):
    return ['INSTALL_BEFORE_CHECKPOINT 0', 'INSTALL_AFTER_CHECKPOINT 0',
            'CHECKPOINT_TIME %d 1' % t, 'CHECKPOINT_SOURCE_BYTES %d' % len(snapshot)]
lines = old[:2] + GUIDANCE + ['SETUP_WAIT_START_TIME 1 1'] + old[2:at]
lines += checkpoint(2) + ['MEASUREMENT_START_TIME 3 1'] + old[at:at + 16]
lines += checkpoint(4) + ['MEASUREMENT_END_TIME 5 1'] + old[at + 16:]
valid = '\n'.join(lines)
assert analyze(valid, [snapshot, snapshot])['idle_branch_passed']
cases = {}
def refusal(name, log, pair):
    r = analyze(log, pair)
    assert not r['idle_branch_passed'] and not r['pending_branch_passed'], name
    cases[name] = r
refusal('short_idle', valid.replace('SETUP_IDLE_OBSERVED_MS 5145', 'SETUP_IDLE_OBSERVED_MS 4999'), [snapshot, snapshot])
refusal('checkpoint_pending', valid.replace('INSTALL_AFTER_CHECKPOINT 0', 'INSTALL_AFTER_CHECKPOINT 258', 1), [snapshot, snapshot])
refusal('altered_same_size_bytes', valid, [snapshot, b'X' + snapshot[1:]])
refusal('wrong_length', valid, [snapshot, snapshot + b'X'])
refusal('missing_checkpoint', valid, [snapshot, None])
refusal('regressed_timestamp', valid.replace('MEASUREMENT_END_TIME 5 1', 'MEASUREMENT_END_TIME 1 1'), [snapshot, snapshot])
refusal('missing_restart', '\n'.join(lines[:-1]), [snapshot, snapshot])
refusal('after_deadline_idle', valid.replace('SETUP_WAIT_ELAPSED_MS 5145', 'SETUP_WAIT_ELAPSED_MS 900000'), [snapshot, snapshot])
refusal('extra_trailing_record', valid + '\nUNEXPECTED', [snapshot, snapshot])
pending = '\n'.join(old[:2] + GUIDANCE + ['SETUP_WAIT_START_TIME 1 1',
    'INSTALL_PREFLIGHT_RESULT 258', 'MEASUREMENT_BLOCKED_SETUP_TIMEOUT 900000'])
assert analyze(pending, [None, None])['pending_branch_passed']
refusal('timeout_has_checkpoint', pending, [snapshot, None])
refusal('short_timeout', pending.replace('900000', '899999'), [None, None])
physical = (k.parent / 'video-setup-physical193/control001/artifacts/physical/after-attempt.log').read_text()
refusal('actual193_old_deadline_not194', physical, [None, None])
result = dict(passed=True, physical_access=False, guest_launch=False,
    synthesized194_idle_using_actual191_lifecycle=True, synthetic194_pending=True,
    actual193_old_deadline_rejected=True, adversarial_cases=cases,
    sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [Path(__file__), k / 'boundary_analysis.py']})
dest.write_text(json.dumps(result, indent=2) + '\n')
print('194 parser accepted exact checkpoint lifecycle/pending and rejected12 boundary adversaries')
