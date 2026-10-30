"""Capture Test843 cold files once after authenticated return. Classify shutdown separately."""
import io,json
from pathlib import Path
import physical004 as h
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
  p=h.R+'/owner843.json';assert h.sha(h.get(f,p))==h.read(K/'stage001.json')['staged'][p]['sha256']
  baseline=dict(h.read(K/'baseline001.json')['critical']);baseline['/E/winnt/system32/ntoskrnl.exe']=pkg['/E/winnt/system32/ntoskrnl.exe']
  for p,v in baseline.items():
   b=get(f,p);same=len(b)==v['bytes'] and h.sha(b)==v['sha256'];r['critical'][p]={'bytes':len(b),'sha256':h.sha(b),'matches_baseline':same}
   if not same or p.lower().endswith('/config/system'):retain(p,b)
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
  trace='/E/winnt/system32/xwn-video-trace.bin'
  b=get(f,trace);retain(trace,b);old=next(v for q,v in pkg.items() if q.lower()==trace.lower());r['retained'][trace]['matches_package']=h.sha(b)==old['sha256']
  r['completed']=True
except BaseException as e:r['error']=repr(e);raise
finally:h.save(out,r)
