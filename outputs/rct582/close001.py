"""Close the failed bounded wait without promoting incomplete input coverage."""
import datetime,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn582/pc001')
read=lambda n:json.loads((K/n).read_text())
state=read('ntfs-phase1.json');cleanup=read('review001.json');integration=read('integration-review001.json');log=(P/'collection001/runner.txt').read_text()
assert state['closed'] and cleanup['passed'] and not integration['passed'] and not read('input-review001.json')['passed']
assert 'title_exposure_timeout=1\n' in log and 'input_sequence_submitted=0\n' in log
ticks=[int(x) for x in re.findall(r'^input_state=title_exposure_wait tick=(\d+)',log,re.M)];assert ticks[-1]-ticks[0]>=90000
out=K/'final001.json';assert not out.exists()
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cleanup_qualified=True,input_qualified=False,late_welcome_qualified=False,early_welcome_close_observed=True,startup_show_unchanged=integration['show_before_after']==[1,1],two_disc_copy_qualified=True,title_exposure_wait_ms=ticks[-1]-ticks[0],blocker='Explorer.EXE tooltips_class32 persisted over the checked lower-left point for the full bounded90second wait',native_captures=0,normal_restart=True,game_exit=0,all_owned_processes_closed=True,physical_access=False,console_unchanged=True,disk_sha256=state['disk_sha256'],preserved_failures=['Exposure timeout; no unknown-window dismissal or guard waiver','Input and late-Welcome integration reviews failed','Screenshot request after automatic VM exit refused by closed guard without QMP access'],next_control='Fresh immutable404 child using exact582 binary/media on1024x768 PC desktop to separate the lower-left shell guidance from the640x480 game client. No closed runtime parent.',limits='No Xbox/input matrix/lateWelcome/save/gameFPS/GPU qualification.',pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.iterdir() if p.is_file() and p.suffix in ['.py','.c','.h','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
