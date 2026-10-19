"""MIT. Close one collected runtime without discarding inconclusive behavior."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
assert read('ntfs-phase1.json')['closed']
assert all(read(n)['passed'] for n in ['review001.json','input-review001.json','display-review001.json'])
assert read('capture-review001.json')['comparisons']['full-drag']['changed']==0
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 input_qualified=False,harness_submission_contract=True,sampled_fullscreen_display_verified=True,
 fullscreen_drag_inconclusive=True,screenshot_notification_interference_hypothesis=True,
 cleanup_qualified=True,physical_access=False,processes_closed=True,no_console_hook=True,
 capture_error='FileNotFoundError; exact event time unrecorded',
 pins={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file() and p.suffix in ['.py','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
