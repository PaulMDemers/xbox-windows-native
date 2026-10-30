"""Create837 controller and baseline metadata before freezing tested source."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-root836'
t=(A/'physical.py').read_text().replace('xwn836','xwn837').replace('XWN16Boot836','XWN16Boot837').replace('xwn-boot836-','xwn-boot837-').replace('owner836','owner837').replace('836physical','837physical')
t=t.replace("['root001','qualify001'","['driver001','driver-host001','driver-review001','qualify001'")
anchor=" return {'freeldr.sys':"
assert t.count(anchor)==1
t=t.replace(anchor," for n,v in read(K/'driver001.json')['artifacts'].items():assert sha((P/'driver001'/n).read_bytes())==v['sha256']\n return {'loader/xwnfatx.sys':(P/'driver001/xwnfatx.sys').read_bytes(),'freeldr.sys':")
t=t.replace('fixed720p Windows boot with FATX root-chain traversal fix','fixed720p Windows boot with isolated FATX cache diagnostic837')
(K/'physical.py').write_text(t)
base=json.loads((A/'baseline001.json').read_text());audit=json.loads((A/'audit001.json').read_text())
assert audit['completed'] and all(v['matches_baseline'] for v in audit['critical'].values())
base['critical']={p:{'bytes':v['bytes'],'sha256':v['sha256']} for p,v in audit['critical'].items()}
base['scope']='Installed Windows baseline unchanged after836. Support from immutable archive; isolated diagnostic xwnfatx only under837 owned boot folder. No runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=16*1024**2
base['projected_console_reserve']['projected_remaining']-=16*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n')
print('837 controller prepared;10 installed Windows baseline files protected')
