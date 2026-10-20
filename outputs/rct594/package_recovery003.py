"""MIT. Pin bounded batch continuation; previous stopped/failed records remain immutable."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((K/'package002.json').read_text());test=json.loads((K/'recovery-host003.json').read_text());batch=json.loads((K/'batch-host001.json').read_text())
assert q['passed'] and test['passed'] and batch['passed']
for p,h in q['pins'].items():assert sha(p)==h,p
for n,h in test['pins'].items():assert sha(K/n)==h,n
assert sha(K/'batch_read001.py')==batch['source_sha256']
st=json.loads((K/'stage002.json').read_text());sup=json.loads((K/'supervisor002-stage.json').read_text())
assert not st['completed'] and not st['temporary_hook_installed'] and not st['writes'] and sup['closed'] and not sup['completed']
assert not (K/'launch001.json').exists()
out=K/'package003.json';assert not out.exists()
q.update(prior_package002_sha256=sha(K/'package002.json'),batch_files_per_connection=16,read_attempts_per_file=2,read_only_recovery_stopped=True)
for p in K.iterdir():
 if p.is_file():q['pins'][str(p.resolve())]=sha(p)
out.write_text(json.dumps(q,indent=2)+'\n');print('Batch recovery package frozen; no physical action')
