"""Close a failed runtime with cleanup and bounded partial findings, not PASS."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');f=read('failure-review001.json')
assert not r['passed'] and r['cleanup_passed'] and f['review_passed'] and not f['runtime_passed']
for n in ['source-review002.json','binary-review001.json','imports-review001.json','media-review001.json','visual-review001.json','process-review001.json','event-timestamps001.json']:assert read(n)['passed'],n
assert read('ntfs-phase1.json')['closed']
out.write_text(json.dumps(dict(closed=True,passed=False,cleanup_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 cause='Recorder rejects NULL ppvBits after successful internal CreateDIBSection return; no park phase.',
 evidence=f,physical_access=False,next='New original absent-output control before a fresh game retry.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('606 CLOSED FAILED; cleanup and partial header observations retained')
