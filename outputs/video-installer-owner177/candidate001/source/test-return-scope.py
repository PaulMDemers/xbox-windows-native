"""Actual return matcher refuses foreign thread/frame at a shared kernel return."""
import hashlib,json
from pathlib import Path
from scope_match import find_return_call
k=Path(__file__).resolve().parent;out=k/'return-scope-tests.json';assert not out.exists()
c=dict(stack=0x123400,stack_delta=8);p={(1,0x82401234):[c]}
assert find_return_call(p,1,0x82401234,0x123408)==c
assert find_return_call(p,2,0x82401234,0x123408) is None
assert find_return_call(p,1,0x82401234,0x123418) is None
assert find_return_call(p,1,0x82401235,0x123408) is None
try:find_return_call({(1,0x82401234):[c,dict(c)]},1,0x82401234,0x123408)
except ValueError:pass
else:raise AssertionError('Ambiguous return must refuse')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out.write_text(json.dumps(dict(passed=True,checks=5,guest_access=False,pins={'scope_match.py':sha(k/'scope_match.py'),'test-return-scope.py':sha(Path(__file__))}),indent=2)+'\n')
print('5 exact return-scope checks PASS')
