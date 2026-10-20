"""MIT. Pin verified staging continuation while retaining the failed package/receipt."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((K/'package001.json').read_text());test=json.loads((K/'recovery-host001.json').read_text())
assert q['passed'] and test['passed']
for p,h in q['pins'].items():assert sha(p)==h,p
for n,h in test['pins'].items():assert sha(K/n)==h,n
st=json.loads((K/'stage001.json').read_text());sup=json.loads((K/'supervisor001-stage.json').read_text())
assert not st['completed'] and not st['temporary_hook_installed'] and sup['closed'] and not sup['completed']
assert not (K/'launch001.json').exists()
out=K/'package002.json';assert not out.exists()
q.update(prior_package_sha256=sha(K/'package001.json'),continuation_of_failed_staging=True,move_and_config_writes_not_replayed=True)
for p in K.iterdir():
 if p.is_file():q['pins'][str(p.resolve())]=sha(p)
out.write_text(json.dumps(q,indent=2)+'\n');print('Recovery package frozen; no physical action')
