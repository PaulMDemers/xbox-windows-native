"""MIT. Freeze runtime and independent image limitations separately."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runtime=json.loads((K/'ntfs-phase1.json').read_text())
review=json.loads((K/'review001.json').read_text())
inputs=json.loads((K/'input-review001.json').read_text())
captures=json.loads((K/'capture-review001.json').read_text())
assert runtime['closed'] and review['passed'] and inputs['passed']
black=['full-options','full-before','full-edge','full-arrow','full-drag']
assert all(captures['captures'][n]['unique_rgb']==1 for n in black)
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),input_qualified=False,harness_submission_contract=True,window_arrow_and_drag_visually_observed=True,window_edge_stationary=True,fullscreen_cases_inconclusive=True,fullscreen_black_capture_tags=black,cleanup_qualified=True,physical_access=False,processes_closed=True,no_console_hook=True,pins={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file() and p.suffix in ['.py','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
