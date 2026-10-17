"""Read-only dashboard ownership, installed code and 720p check; no launch."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import connect,baseline,get,names,sha,utc,START,NORMAL,TARGET
out=K/'console-check001.json';assert not out.exists()
r=dict(utc=utc(),passed=False,physical_writes=False,launch_requested=False,console_C_accessed=False)
try:
 with connect(timeout=8) as f:
  baseline(f,'720p')
  r['startup_listing']=names(f,START)
  r['normal_startup_sha256']=sha(get(f,NORMAL));r['launcher_sha256']=sha(get(f,TARGET))
  r['passed']=True
except Exception as e:r['failure']=type(e).__name__+': '+str(e)
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
