"""Preserve failed copy admission without promoting it to game evidence."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('failure-review001.json');assert r['review_passed'] and r['cleanup_passed'] and not r['runtime_passed']
for n in ['source-review001.json','binary-review001.json','imports-review001.json','media-review001.json','process-review001.json','event-timestamps001.json']:
 assert read(n)['passed'],n
out.write_text(json.dumps(dict(closed=True,passed=False,cleanup_passed=True,game_launched=False,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,evidence=r,
 next='Fresh609 with exact copy-script tool-reference validation and corrected uppercase TRACE namespace.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('608 CLOSED FAILED before game launch')
