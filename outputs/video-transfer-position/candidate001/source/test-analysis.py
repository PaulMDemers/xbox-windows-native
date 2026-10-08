"""Reject incomplete isolation/measurement evidence; never synthesize a guest PASS."""
import copy
import json
from analyze import k, case, read, sha, summarize
names = ['verification.json', 'performance-lease.json', 'lease-check.json', 'closure.json', 'launch.json']
inputs = [read(case/n) for n in names]
assert summarize(*inputs)['passed']
mutations = [
    (0, 'timing_qualified', False), (1, 'finished', False),
    (1, 'build_held', False), (2, 'build_conflict', False),
    (2, 'xemu_conflict', False), (2, 'instance_pid', -1),
    (2, 'checked_utc', '2030-01-01T00:00:00Z'),
]
for index, key, value in mutations:
    changed = copy.deepcopy(inputs); changed[index][key] = value
    try: summarize(*changed)
    except AssertionError: pass
    else: raise AssertionError(key)
changed = copy.deepcopy(inputs); changed[0]['cases'].pop()
try: summarize(*changed)
except AssertionError: pass
else: raise AssertionError('missing repetition')
r = dict(passed=True, failure_gates_checked=8, synthetic_mutations_only=True,
         pins={n:sha(k/n) for n in ['analyze.py','test-analysis.py']})
(k/'analysis-tests.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Eight isolation/completeness failure gates rejected')
