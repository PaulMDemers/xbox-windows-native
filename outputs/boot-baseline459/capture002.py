"""Read-only collection after the user-reported normal cold-start return."""
import json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/boot-baseline459/capture002'
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,names,sha,utc,write_json,START,NORMAL,TARGET
out=K/'capture002.json';assert not out.exists() and not P.exists()
assert shutil.disk_usage(W).free-32*1024**2>=20*1024**3
P.mkdir();previous=json.loads((K.parent/'d3d-direct458/physical001-collection.json').read_text())
r=dict(utc=utc(),completed=False,remote_writes=[],host_launch_sent=False,console_C_accessed=False,
 user_report='It just rebooted straight to the dash',requested_protocol='Full power off/on then one normal direct File Explorer launch with no test hook',
 power_off_duration_independently_verified=False,windows_boot_proved=False,files={})
write_json(out,r)
try:
 with connect() as f:
  baseline(f,'720p');listing=names(f,START)
  assert {n.lower() for n in listing}<={'xwnsetup.cmd','desktop.ini'};r['startup_listing']=listing
  for n in [NORMAL,TARGET,'/E/winnt/system32/xwn-video-trace.bin']+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]:
   b=get(f,n);assert b==get(f,n);p=P/n.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   row=dict(path=str(p),bytes=len(b),sha256=sha(b))
   if n in previous['files']:row['unchanged_since458']=row['sha256']==previous['files'][n]['sha256']
   r['files'][n]=row;write_json(out,r)
  r.update(completed=True,mode='720p',no_test_hook=True,ended_utc=utc());write_json(out,r)
except BaseException as e:r['failure']=repr(e);write_json(out,r);raise
print(json.dumps(dict(completed=True,files=len(r['files']),all_compared_unchanged=all(v.get('unchanged_since458',True) for v in r['files'].values()),remote_writes=[])))
