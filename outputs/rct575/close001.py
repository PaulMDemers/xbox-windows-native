"""MIT. Freeze the qualified PC probe, distinct from any physical result."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
runtime=read('ntfs-phase1.json');assert runtime['closed'] and runtime['exit_code']==0
assert not any(runtime.get(n) for n in ['host_quit','deadline','capture_errors'])
for n in ['review001.json','input-review001.json','display-review001.json','notification-review001.json']:assert read(n)['passed'],n
c=read('capture-review001.json')['comparisons'];assert c['window-edge']['changed']==0
assert all(c[n]['changed']>0 for n in ['window-arrow','window-drag','full-edge','full-arrow','full-drag'])
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 input_qualified=True,harness_submission_contract=True,sampled_fullscreen_display_verified=True,
 window_edge_stationary=True,window_arrow_and_drag_visually_observed=True,
 fullscreen_edge_arrow_and_drag_visually_observed=True,cleanup_qualified=True,
 physical_access=False,processes_closed=True,no_console_hook=True,
 limits='PC probe qualification only. Screenshot settling supports, but does not uniquely prove, notification interference.',
 pins={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file() and p.suffix in ['.py','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
