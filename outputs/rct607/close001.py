"""Close the original NT5 absent-output control after independent cold checks."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read('review001.json');s=read('ntfs-phase1.json');assert r['passed'] and s['closed']
for n in ['binary-review001.json','source-review001.json','media-review001.json','oracle-tests001.json','phase-oracle-tests001.json','absent-tests001.json','event-timestamps001.json','process-review001.json']:
 assert read(n)['passed'],n
out.write_text(json.dumps(dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 physical_access=False,game_access=False,trace=r['trace'],normal_shutdown_delta=1,
 subject_control_equal=True,new_system_events=r['new_system_events'],capture_errors=s.get('capture_errors',[]),
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 scope='Original NT5 control validates successful RGB/BI_BITFIELDS objects and invalid-header failure with NULL ppvBits. OUTPUT_ABSENT records absence, not an invented pointer. Other pointer checks remain strict.',
 limits='No new actual-game result, timing, FPS or Xbox acceleration. BI_BITFIELDS decoding remains unsupported.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n',encoding='utf-8')
print('607 CLOSED: original absent-output control and independent checks passed')
