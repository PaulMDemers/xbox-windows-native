"""Close incomplete PC581 without promoting failed input or late-arrival checks."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text())
state=read('ntfs-phase1.json');review=read('review001.json');integration=read('integration-review001.json');inputs=read('input-review001.json')
assert state['closed'] and review['passed'] and not integration['passed'] and not inputs['passed']
assert read('collection001.json')['completed'] and read('ntfs-cold1-002.json')['normal_shutdown_delta']==1
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cleanup_qualified=True,input_qualified=False,late_welcome_qualified=False,early_welcome_close_observed=True,startup_show_unchanged=True,two_disc_copy_qualified=True,all502_prelaunch_integrity_verified=True,both_media_ejected=True,title_ready_observed=True,blocker='Explorer.EXE tooltips_class32; private passive image shows Start-button guidance balloon over lower-left game corner',native_captures=0,game_exit=0,no_forced_game_termination=True,normal_restart=True,all_owned_processes_closed=True,physical_access=False,console_state='unchanged since closed576; last verified dashboard, no hook or launch outstanding',disk_sha256=state['disk_sha256'],preserved_failures=['Initial display confirmation reverted; observed800x600 accepted before game','Missing --phase login call refused before input','WSL argv stripped backslashes from single-word launch; executable not found. Corrected cmd /c inspected before one actual game launch','Passive screen request after VM exit refused by closed-state guard; no QMP access','Late-Welcome and input qualification review failed; no test-case capture reached'],limits='No Xbox, scrolling matrix, delayed Welcome, save persistence, sound, FPS or GPU claim.',pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file() and p.suffix in ['.py','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
