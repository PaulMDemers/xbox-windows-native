"""Host-only gate adversaries; the unobserved197 row is synthetic, not guest evidence."""
import copy
import hashlib
import json
from pathlib import Path
from prerequisite_policy import qualified_branches

k = Path(__file__).resolve().parent
dest = k / 'prerequisite-tests.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
paths = [k.parent / 'video-measurement-boundary194/idle001/audit.json',
         k.parent / 'video-measurement-boundary194/pending001/audit.json',
         k.parent / 'video-boundary-boot196/pending002/audit.json']
idle, failed, observed = [read(p) for p in paths]
ordinary = dict(observed, case='pending001', debugger=False)
rows = [idle, failed, observed, ordinary]
assert qualified_branches(*rows)
checks = [dict(name='Host synthesized ordinary row accepted for predicate only', passed=True)]
for index, field, value in [
    (0, 'integrity_passed', False), (0, 'idle_branch_passed', False),
    (0, 'debugger', True), (1, 'diagnostic_usable', True),
    (2, 'snapshot_transactions_passed', False), (2, 'debugger', False),
    (3, 'debugger', True), (3, 'pending_branch_passed', False),
    (3, 'integrity_passed', False), (3, 'diagnostic_usable', False),
    (3, 'dashboard_return', True), (3, 'normal_shutdown_count', 1),
    (3, 'ordinary_qualified', True), (3, 'physical_qualified', True),
    (3, 'case', 'pending002')]:
    test = copy.deepcopy(rows)
    test[index][field] = value
    assert not qualified_branches(*test)
    checks.append(dict(name='Reject row%d %s=%r' % (index, field, value), passed=True))
for index in range(4):
    test = copy.deepcopy(rows)
    test[index] = {}
    assert not qualified_branches(*test)
    checks.append(dict(name='Reject absent row%d' % index, passed=True))
dest.write_text(json.dumps(dict(passed=True, physical_access=False, guest_launch=False,
    actual197_evidence=False, synthetic_ordinary_row=True, checks=checks,
    source_pins={p.name:sha(p) for p in [k/'prerequisite_policy.py', Path(__file__)]},
    input_pins={p.relative_to(k.parents[1]).as_posix():sha(p) for p in paths}), indent=2)+'\n', encoding='utf-8')
print('20 host prerequisite cases passed; no actual197 runtime or physical readiness')
