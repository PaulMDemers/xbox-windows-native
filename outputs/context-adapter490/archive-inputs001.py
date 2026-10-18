"""Archive exact package inputs after runtime closure, before future source edits."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn490/frozen001');out=K/'archived-inputs001.json'
assert not P.exists() and not out.exists()
package=json.loads((K/'package001.json').read_text());state=json.loads((K/'physical001-collection.json').read_text())
assert state['completed'] and state['hook_removed'];P.mkdir();rows=[]
for i,(name,h) in enumerate(sorted(package['dependencies'].items())):
    p=Path(name);data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==h
    dest=P/f'{i:03d}-{p.name}';dest.write_bytes(data);assert dest.read_bytes()==data
    rows.append(dict(original=name,path=str(dest),sha256=h))
out.write_text(json.dumps(dict(passed=True,rows=rows),indent=2)+'\n');print('Archived package inputs:',len(rows))
