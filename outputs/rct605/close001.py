"""Close605 after original control, corrected independent review and cold checks."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read('review002.json');s=read('ntfs-phase1.json');assert r['passed'] and s['closed']
for n in ['host-phase001.json','binary-review001.json','source-review001.json','media-review001.json','oracle-tests002.json','phase-oracle-tests002.json','event-timestamps001.json']:assert read(n)['passed'],n
out.write_text(json.dumps(dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_access=False,
 trace=r['trace'],normal_shutdown_delta=1,subject_control_equal=True,new_system_events=r['new_system_events'],capture_errors=s.get('capture_errors',[]),
 console_state='Untouched; last dashboard/no owned hook.596 SOFTWARE cleanup remains cold-only.',
 correction='Frozen checker reused WORDS marker as sampling phase; corrected offline checker002 renames that local only. Runtime and expected outcomes unchanged; original preserved.',
 limits='Original NT5 control qualifies latched phase signaling and capped header sampling. No game layout, costs, FPS or Xbox acceleration.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()}),indent=2)+'\n')
print('605 CLOSED: latched phase and capped original graphics samples passed')
