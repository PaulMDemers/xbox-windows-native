import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
paths=[Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2'),Path('/mnt/c/xwn403/install-restore002/restored.qcow2')];snap=[]
for p in paths:
 with ColdIO(p) as io:
  w=m.Writer(io,m.fatx.open_partition(io,p,'E'));rows={}
  for name in ['tdata','udata']:
   entry=w.directory(1)['entries'][name][2];at=int.from_bytes(entry[44:48],'little');rows[name]={'entry':entry.hex(),'clusters':[{'index':c,'sha256':m.sha(w.read_cluster(c)),'fat':w.fat[c]} for c in w.chain(at)]}
  snap.append(rows)
r={'unchanged':snap[0]==snap[1],'factory_directories':snap,'scope':'Exact retained TDATA/UDATA directory cluster bytes/FAT/entries from unused stock image'}
assert r['unchanged'];(K/'factory-roots001.json').write_text(json.dumps(r,indent=2)+'\n');print('Factory roots byte-exact')
