"""Read-only boot-chain/startup capture after failed inventory launches."""
import hashlib,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/boot-baseline459/capture001'
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,names,sha,utc,write_json,START,NORMAL,TARGET
out=K/'capture001.json';assert not out.exists() and not P.exists()
assert shutil.disk_usage(W).free-32*1024**2>=20*1024**3
P.mkdir(parents=True)
r=dict(utc=utc(),completed=False,remote_writes=[],launch_requested=False,console_C_accessed=False,files={},listings={})
write_json(out,r)
try:
 with connect() as f:
  baseline(f,'720p')
  for d in ['/E/Applications/XWNEBoot','/E/Applications/XWNEBoot/loader',START]:
   r['listings'][d]=names(f,d)
  assert set(n.lower() for n in r['listings'][START])<={'xwnsetup.cmd','desktop.ini'}
  selected=[TARGET,'/E/Applications/XWNEBoot/freeldr.sys','/E/Applications/XWNEBoot/rosload.exe',
   '/E/Applications/XWNEBoot/freeldr.ini','/E/Applications/XWNEBoot/loader/halxboxnt5.dll',
   '/E/Applications/XWNEBoot/loader/xboxbvid.dll',NORMAL]
  for n in selected:
   b=get(f,n);assert b==get(f,n)
   p=P/n.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   r['files'][n]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  n='/E/winnt/system32/xwn-video-trace.bin';b=get(f,n,True)
  if b is not None:
   assert b==get(f,n);p=P/'xwn-video-trace.bin';p.write_bytes(b)
   r['files'][n]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  r.update(completed=True,mode='720p',temporary_startup_absent=True,ended_utc=utc())
  write_json(out,r)
except BaseException as e:r['failure']=repr(e);write_json(out,r);raise
print(json.dumps(dict(completed=True,files=len(r['files']),mode='720p',temporary_startup_absent=True,remote_writes=[])))
