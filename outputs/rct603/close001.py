"""Close603 after exact cold comparison and direct private image inspection."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=read('review001.json');s=read('ntfs-phase1.json')
assert r['passed'] and r['scene']['passed'] and s['closed'] and s['exit_code']==0
for name in ['scene-tests001.json','source-review002.json','binary-review001.json','asset-header-review001.json','media-review001.json','setup-review001.json']:
 assert read(name)['passed']
visual=dict(passed=True,method='Assistant directly inspected private captures: Window mode, paused Forest Frontiers, deliberate displaced view, Load Game menu, restored entrance/path/trees, and stable subsequent loaded view. Exact interior comparison supplies camera/zoom agreement; this does not verify every serialized game value.',
 captures={v['name']:sha(Path(v['path'])) for v in r['captures']})
(K/'visual-review001.json').write_text(json.dumps(visual,indent=2)+'\n')
final=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,game_instrumentation=False,
 scene=r['scene'],save=r['save'],registry_restored=True,normal_shutdown_delta=1,new_system_events=r['new_system_events'],
 capture_errors=s.get('capture_errors',[]),preserved_failures=['build001 -Werror misleading-indentation; corrected in distinct002 sources'],
 console_state='Untouched; last dashboard with no owned hook.596 offline SOFTWARE cleanup still cold-only.',
 limits='Fresh PC load of retained PC593 save and exact scenery restoration. Not the different physical594 save, complete serialization proof, game FPS, timing overhead or acceleration.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()})
out.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
print('603 CLOSED: exact retained PC593 scenery restored after deliberate camera move')
