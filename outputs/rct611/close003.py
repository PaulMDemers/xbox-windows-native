"""Close space-aborted611 after preservation, process closure and byte archives."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
for n in ['failure-review002.json','process-review001.json']:assert read(n)['passed']
assert read('archive001.json')['completed']
s=read('ntfs-phase1.json');assert s['closed'] and s['space_stop']
out.write_text(json.dumps(dict(closed=True,passed=False,cleanup_passed=False,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,
 evidence=read('failure-review002.json'),archive=read('archive001.json'),
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 scope='Host space guard terminated the VM; no game outcome or normal restart qualified. Historical602/606/608/609 leaf bytes archived losslessly on E; no evidence discarded.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
