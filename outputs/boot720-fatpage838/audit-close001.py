"""Cold readback after user power cycle. Preserve835-derived installation baseline."""
import io,json
from pathlib import Path
import physical as h
K=h.K;P=h.P;out=K/'audit001.json';assert not out.exists()
assert h.read(K/'collection001.json')['completed'] and h.read(K/'dashboard001.json')['authenticated']
pkg=h.read(h.W/'outputs/boot720-native835/package001.json')['files']
r={'utc':h.utc(),'completed':False,'hook':'none installed','critical':{},'inventory':{},'retained':{},'user_reported_dashboard_return':True};h.save(out,r)
d=P/'audit001';d.mkdir()
def listing(f,p):
 assert p in ['/E/winnt','/E/winnt/system32/config']
 f.cwd(p);assert f.pwd().replace('\\','/').rstrip('/').lower()==p.lower()
 rows=[];f.retrlines('LIST',rows.append);rows=[v.split(None,8) for v in rows];assert all(len(v)==9 for v in rows)
 return {v[8]:{'directory':v[0][0]=='d','bytes':int(v[4])} for v in rows if v[8] not in ['.','..']}
def get(f,p):
 assert p.startswith('/E/winnt/') or p in h.read(K/'baseline001.json')['critical'] or p in r.get('new_root_files',{})
 b=io.BytesIO()
 def take(v):assert b.tell()+len(v)<=16*1024**2;b.write(v)
 f.retrbinary('RETR '+p,take,65536);return b.getvalue()
def retain(p,b):
 dest=d/p.removeprefix('/E/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 r['retained'][p]={'bytes':len(b),'sha256':h.sha(b),'private_path':str(dest)}
try:
 with h.connect() as f:
  p=h.R+'/owner838.json';assert h.sha(h.get(f,p))==h.read(K/'stage001.json')['staged'][p]['sha256']
  baseline=dict(h.read(K/'baseline001.json')['critical']);baseline['/E/winnt/system32/ntoskrnl.exe']=pkg['/E/winnt/system32/ntoskrnl.exe']
  for p,v in baseline.items():
   b=get(f,p);same=len(b)==v['bytes'] and h.sha(b)==v['sha256'];r['critical'][p]={'bytes':len(b),'sha256':h.sha(b),'matches_baseline':same}
   if not same:retain(p,b)
   h.save(out,r)
  for p in ['/E/winnt','/E/winnt/system32/config']:r['inventory'][p]=listing(f,p)
  before={n.lower() for n in h.read(K/'stage001.json')['before_e']}
  now=h.names(f,'/E');r['new_root_files']={'/E/'+n:v for n,v in now.items() if n.lower() not in before and not n.startswith(h.PREFIX) and not v['directory']}
  for p,v in r['new_root_files'].items():
   if v['bytes']<=16*1024**2:retain(p,get(f,p))
  for folder,rows in r['inventory'].items():
   for n,v in rows.items():
    if not v['directory'] and n.lower().endswith(('.log','.evt','.txt','.dmp')) and v['bytes']<=16*1024**2:
     p=folder+'/'+n;b=get(f,p);retain(p,b)
     old=next((v for q,v in pkg.items() if q.lower()==p.lower()),None)
     r['retained'][p]['matches_package']=bool(old and h.sha(b)==old['sha256'])
  r['completed']=True
except BaseException as e:r['error']=repr(e);raise
finally:h.save(out,r)
c=h.read(K/'collection001.json');last=list(c['reports'].values())[-1]['data']
assert last['sdk_mode']==[1280,720,32,60] and last['framebuffer']['admitted']
closed={'utc':h.utc(),'state':'CLOSED','result':'Diagnostic E8380001 in ReadVolumeLabel: root FCB one-cluster EOF overrun; no desktop',
 'evidence':['screen001.json','collection001.json','audit001.json'],
 'console':'Authenticated UnleashX after user-reported dashboard return','host_runtime':'none owned','hook':'none installed',
 'next':'Fresh839 bounded root-chain size and traversal repair; no relaunch/recollection/runtime parenting838'}
h.save(K/'closed001.json',closed)
print(json.dumps({'closed':closed,'critical_changes':[p for p,v in r['critical'].items() if not v['matches_baseline']],
 'new_root_files':r['new_root_files'],'changed_logs':[p for p,v in r['retained'].items() if not v.get('matches_package',True)]},indent=2))
