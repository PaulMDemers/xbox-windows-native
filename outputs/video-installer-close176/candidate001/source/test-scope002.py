"""Actual scope selector tests: equal numeric handles in other tables cannot match."""
import hashlib,json
from pathlib import Path
from scope_match import find_close_scope
k=Path(__file__).resolve().parent;p=k/'scope-tests002.json';assert not p.exists()
s={'process':0x81230000,'thread':0x82340000,'token_handle':1864};scopes={s['thread']:s}
assert find_close_scope(scopes,s['process'],1864)==s
assert find_close_scope(scopes,0x81230004,1864) is None
assert find_close_scope(scopes,s['process'],1868) is None
assert find_close_scope({},s['process'],1864) is None
try:find_close_scope({1:s,2:dict(s)},s['process'],1864)
except ValueError:pass
else:raise AssertionError('Ambiguity must refuse')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p.write_text(json.dumps(dict(passed=True,checks=5,guest_access=False,pins={'scope_match.py':sha(k/'scope_match.py'),'test-scope.py':sha(Path(__file__))}),indent=2)+'\n')
print('5 actual scope-selector checks PASS')
