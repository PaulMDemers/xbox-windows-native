"""Close only after actual game, independent scene/trace and cleanup checks."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');assert r['passed'] and r['cleanup_passed']
for n in ['source-review001.json','binary-review001.json','imports-review001.json','media-review001.json',
          'copy-contract-tests001.json','scene-tests001.json','oracle-tests001.json','visual-review001.json',
          'layout-review001.json','process-review001.json','event-timestamps001.json']:
 assert read(n)['passed'],n
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
out.write_text(json.dumps(dict(closed=True,passed=True,cleanup_passed=True,
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_launched=True,
 evidence=r,layout=read('layout-review001.json'),capture_errors=s.get('capture_errors',[]),
 scope='Instrumented PC saved-scene graphics sample. No timings, frame count, FPS or Xbox acceleration.',
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('609 CLOSED: actual saved-scene trace and cleanup passed')
