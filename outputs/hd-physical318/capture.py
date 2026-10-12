"""READ ONLY physical preflight; preserve actual rollback, hives, events and INF state."""
from common001 import *
dest=k/'capture001.json';assert not dest.exists()
folder=k/'artifacts/before001';assert not folder.exists()
ticket();package=read(k/'package.json')
with connect(timeout=8) as f:
 check_fixed(f);assert get(f,startup)==c.incoming(startup)
 assert 'xwnhd318' not in {n.lower() for n in names(f,'/F')}
 r=dict(created_utc=utc(),physical_access=True,physical_writes=False,completed=False,files={},inventories={});save(dest,r)
 paths=list(fixed())+[v['path'] for v in package['video']]+[startup,'/F/winnt/setupapi.log','/F/winnt/system32/xwn-video-trace.bin']
 for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:paths.append('/F/winnt/system32/config/'+n)
 r['inventories']['/F/winnt/inf']=names(f,'/F/winnt/inf')
 for n,row in r['inventories']['/F/winnt/inf'].items():
  if not row['directory']:paths.append('/F/winnt/inf/'+n)
 for p in dict.fromkeys(paths):
  data=get(f,p);r['files'][p]=keep(folder,p,data)
  if '/config/' in p:assert get(f,p)==data,'Cold hive/event changed'
  save(dest,r)
 r.update(completed=True,completed_utc=utc());save(dest,r)
print('Read-only physical capture complete; no deployment')
