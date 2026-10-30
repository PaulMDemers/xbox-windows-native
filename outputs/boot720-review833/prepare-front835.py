"""Source-only reuse of kernel720p frontend and checked bridge, new Windows boot ID."""
import hashlib,json
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/boot720-native835';old=W/'outputs/loader-repeat831'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
for name in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','plan_test.py','bridge.S','fixture.S','link.ld','host005.py','cpu004.py','build001.py']:
 p=old/name;pins[name]=sha(p);data=p.read_bytes()
 if p.suffix=='.py':
  data=data.replace(b'xwn831',b'xwn835').replace(b'831',b'835')
  data=data.replace(b"K/'firmware/build001.json'",b"K/'chain001.json'").replace(b'firmware001/image-crom.bin',b'chain001/image-crom.bin')
 elif name=='main.c':
  data=data.replace(b'xwn-mode831-',b'xwn-boot835-').replace(b'Xromwell830',b'Windows835').replace(b'Deliberate power-cycle hold.',b'Fixed720p retained-mode Windows boot.')
 elif name=='Makefile':data=data.replace(b'831',b'835').replace(b'830',b'835')
 (K/name).write_bytes(data)
(K/'front-reuse001.json').write_text(json.dumps({'source_only':True,'parent_pins':pins,'changes':'Fresh835 reports/title and firmware input. Bridge/page/plan/layout exact source bytes retained.'},indent=2)+'\n')
