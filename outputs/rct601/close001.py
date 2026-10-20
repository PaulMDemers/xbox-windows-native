"""Close601 after the corrected raw-event review; preserve every earlier result."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=['review002.json','event-review001.json','oracle-tests001.json','host-tests001.json','binary-review001.json','media-review001.json']
assert all(read(n)['passed'] for n in checks)
s=read('ntfs-phase1.json');assert s['closed'] and s['exit_code']==0
r=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,
 trace=read('review002.json')['trace'],normal_shutdown_delta=1,event_correction='event-review001.json',
 failures_preserved=['build001: incompatible FARPROC cast under -Werror','review001: copied6016 shutdown-count predicate','periodic screenshot FileNotFoundError racing process_exit0'],
 capture_errors=s.get('capture_errors',[]),new_system_events=read('review002.json')['new_system_events'],
 console_state='Untouched; last dashboard with no owned hook.596 offline SOFTWARE cleanup remains cold-only.',
 limits='Original NT5 PC graphics/recorder control, no retail game, no Xbox acceleration or performance result.60.1second actual recorder bound; no bound reached.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print('601 CLOSED:106 paired calls, real GDI pixels and DirectDraw objects passed')
