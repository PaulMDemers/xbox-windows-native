"""Close after the actual saved-scene costs, visual review and cleanup gates."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');assert r['passed'] and r['cleanup_passed']
for n in ['host-tests001.json','inheritance-review001.json','binary-review001.json','media-review001.json',
 'copy-contract-tests001.json','scene-tests001.json','visual-review001.json',
 'process-review001.json','event-timestamps002.json']:
 assert read(n)['passed'],n
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
h=read('serial-host001.json');assert h['closed'] and not h.get('error')
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=True,
 evidence=r,capture_errors=s.get('capture_errors',[]),
 scope='Uninstrumented paused PC saved-scene process costs with counter observer. Not game FPS, Xbox performance, acceleration or tracer overhead.',
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
