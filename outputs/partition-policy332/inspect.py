"""Read only dashboard E/F directory and transfer replies; never touch C."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,utc
out=K/'dashboard001.json';assert not out.exists()
r=dict(started_utc=utc(),physical_writes=False,console_c_accessed=False,partitions={})
with connect(timeout=8) as f:
    for path in ['/E','/F']:
        f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
        lines=[];reply=f.retrlines('LIST',lines.append)
        entries=[v.split(None,8) for v in lines]
        assert all(len(v)==9 for v in entries)
        r['partitions'][path]=dict(reply=reply,entries=[dict(name=v[8],directory=v[0].startswith('d'),bytes=int(v[4])) for v in entries if v[8] not in ['.','..']])
r['completed_utc']=utc();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({p:dict(reply=v['reply'],entries=len(v['entries']),directories=[x['name'] for x in v['entries'] if x['directory']]) for p,v in r['partitions'].items()},indent=2))
