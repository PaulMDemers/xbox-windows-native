"""Close original module lifetime control after exact independent checks."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');s=read('ntfs-phase1.json');assert r['passed'] and s['closed']
for n in ['host-tests001.json','binary-review001.json','source-review001.json','media-review001.json','oracle-tests001.json','phase-oracle-tests001.json','absent-tests001.json','lifetime-oracle-tests001.json','event-timestamps002.json','process-review001.json']:
 assert read(n)['passed'],n
out.write_text(json.dumps(dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 physical_access=False,game_access=False,trace=r['trace'],normal_shutdown_delta=1,
 subject_control_equal=True,new_system_events=r['new_system_events'],capture_errors=s.get('capture_errors',[]),
 scope='Original NT5 A/B/A DLL unload/reload at the same base and return address. Fresh generation ownership and restored 90/f8/90 instruction bytes; all calls paired; pristine and traced logs equal.',
 limits='No actual-game, timing, FPS or Xbox acceleration result. Conservative rejection of any pending call/step/held thread remains.',
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('610 CLOSED: original lifetime control passed')
