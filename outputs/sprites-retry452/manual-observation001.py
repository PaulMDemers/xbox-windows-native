"""Read-only observation after user manual boots, separate from closed451."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,names,sha,utc,write_json,START,NORMAL,TARGET
out=K/'manual-observation001.json';assert not out.exists()
P=W/'work/sprites-manual452-observation001';assert not P.exists();P.mkdir()
previous=json.loads((K.parent/'sprites-xbox451/physical001-collection.json').read_text())
r=dict(utc=utc(),completed=False,remote_writes=[],console_C_accessed=False,
 user_report="i booted it three times, the first one might have failed to launch idk really - it was just back at the dash. Boots 2&3 worked fine. Rebooted. It’s back at the dash now.",
 confirmed_successful_manual_boots=2,first_attempt='uncertain',sample_qualification=False,files={})
write_json(out,r)
with connect(timeout=5) as f:
 baseline(f,'720p');listing=names(f,START)
 assert {n.lower() for n in listing}<={'desktop.ini','xwnsetup.cmd'}
 r['startup_listing']=listing
 for path in [NORMAL,TARGET]+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]:
  data=get(f,path);assert data==get(f,path)
  dest=P/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  row=dict(path=str(dest),bytes=len(data),sha256=sha(data))
  if path in previous['files']:row['unchanged_since451_collection']=row['sha256']==previous['files'][path]['sha256']
  r['files'][path]=row;write_json(out,r)
 r.update(completed=True,ended_utc=utc(),baseline_720p_exact=True);write_json(out,r)
print('Manual observation preserved; no remote writes or test qualification.')
