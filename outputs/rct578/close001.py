"""Close the PC Save dialog inspection, retaining all failed review attempts."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text())
runtime=read('ntfs-phase1.json');assert runtime['closed'] and runtime['exit_code']==0
assert not any(runtime.get(n) for n in ['host_quit','deadline','capture_errors','space_stop'])
assert read('review001.json')['passed'] and read('dialog-review001.json')['passed']
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),dialog_inspection_qualified=True,cleanup_qualified=True,normal_restart=True,all_owned_processes_closed=True,physical_access=False,saved_game_created=False,save_reload_qualified=False,transport_iso_retained_as_private_asset=True,preserved_failure='review-attempt001: host-path review invoked under WSL; failed before output, corrected host invocation without rerunning guest or cold collection',limits='Save dialog inspection/cancel only. No Xbox result, game persistence or performance qualification.',pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(K.iterdir()) if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
