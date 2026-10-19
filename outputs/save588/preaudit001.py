"""Read-only audit of the new588 prelaunch hive capture; no console access."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
before=json.loads((K/'before.json').read_text());assert before['completed']
out=K/'preaudit001.json';assert not out.exists()
result={}
for name in ('system','software','sam','security','default'):
 row=before['files']['/E/winnt/system32/config/'+name]
 s=row['path'];p=Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/'))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 result[name]=audit(p)
r=dict(hives=result,passed=all(v['header_valid'] and v['clean'] and v['independent_raw_values_agree'] for v in result.values()),
 scope='Fresh captured prelaunch hives only. Known typed decode limitations retained; no full disk allocation audit.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'hives':len(result)}));assert r['passed']
