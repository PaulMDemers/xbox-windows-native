"""Copy retained source inputs only; no closed runtime is opened."""
import json,hashlib,urllib.request,datetime
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; O=Path('C:/xwn704/source001')
assert not O.exists(); O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'physical_access':False,'copies':{},'lookups':[]}
for name,parent in [('gpu_legacy.c','xcal-geometry702'),('gpu_types.h','xcal-geometry702'),
 ('xcal_bus.c','xcal-sequence700'),('xcal_bus.h','xcal-sequence700'),
 ('xcal_table.h','xcal-sequence700'),('delay_candidate.h','xcal-sequence700')]:
 p=W/'outputs'/parent/name; q=K/name; assert not q.exists(); q.write_bytes(p.read_bytes())
 r['copies'][name]={'source':str(p.relative_to(W)),'sha256':sha(q)}
for name in ['BootVgaInitialization.c','VideoInitialization.c','xcalibur.c']:
 p=Path('C:/xwn700/source001')/name; q=O/name; q.write_bytes(p.read_bytes())
 r['copies'][name]={'source':str(p),'sha256':sha(q)}
for name in ['hw.h','hw.c','nvreg.h']:
 url='https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/dispnv04/'+name
 try:
  data=urllib.request.urlopen(url,timeout=20).read();q=O/name;q.write_bytes(data)
  r['lookups'].append({'url':url,'sha256':sha(q),'bytes':len(data),'path':str(q)})
 except Exception as e:r['lookups'].append({'url':url,'failure':repr(e)})
r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(K/'sources001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r['lookups'],indent=2))
