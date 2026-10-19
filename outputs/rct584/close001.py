"""Close this single PC control without promoting incomplete input evidence."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final001.json';assert not out.exists()
runtime=read('ntfs-phase1.json');cleanup=read('review001.json')
integration=read('integration-review001.json');inputs=read('input-review001.json')
captures=read('capture-review001.json');assert runtime['closed']
qualified=False
if inputs['passed'] and integration['passed']:
    visual=read('visual-review001.json');notification=read('notification-review001.json')
    qualified=visual['passed'] and notification['passed']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       cleanup_qualified=cleanup['passed'],input_qualified=qualified,
       late_welcome_qualified=integration['passed'],
       initial_desktop=[1024,768],unchanged_binary_probe=582,
       native_captures=len(captures['captures']),
       startup_show_unchanged=integration['checks']['show_unchanged'],
       two_disc_copy_qualified=integration['checks']['all_assets_preverified'] and integration['checks']['both_media_ejected'],
       all_owned_processes_closed=True,physical_access=False,console_unchanged=True,
       disk_sha256=runtime['disk_sha256'],
       failed_checks={label:[n for n,v in record['checks'].items() if not v] for label,record in [('cleanup',cleanup),('input',inputs),('integration',integration)]},
       limits='PC control only. No Xbox scrolling/fullscreen, save persistence, game FPS, sound or GPU qualification.',
       pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and p.suffix in ['.py','.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['closed','cleanup_qualified','input_qualified','late_welcome_qualified','native_captures']}))
