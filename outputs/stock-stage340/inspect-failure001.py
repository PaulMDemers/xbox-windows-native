"""Read only the journaled uncertain file after the original FTP failure."""
import json,sys
from pathlib import Path
from engine import digest,LAUNCHER
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'demo-audio-level256'))
from common001 import connect,get,names,utc
r=json.loads((K/'physical001.json').read_text());assert r['quarantined'] and not r['complete']
j=Path('E:/xwn340/stage001/journal.jsonl').read_bytes();assert digest(j)==r['journal_sha256']
rows=[json.loads(x) for x in j.splitlines()];last=rows[-1];assert last['kind']=='write_intent'
p=last['path'];assert p!=LAUNCHER
b=(Path('E:/xwn337/package001')/p.lstrip('/')).read_bytes();assert digest(b)==last['meta']['sha256']
dest=K/'failure-inspection001.json';private=Path('E:/xwn340/failure001');assert not dest.exists() and not private.exists();private.mkdir()
with connect() as f:
    actual=get(f,p,optional=True)
    if actual is not None:(private/'uncertain-file.bin').write_bytes(actual)
    folder,name=LAUNCHER.rsplit('/',1);launcher_absent=name.lower() not in {n.lower() for n in names(f,folder)}
result=dict(utc=utc(),path=p,expected_bytes=len(b),actual_bytes=None if actual is None else len(actual),
            exact=actual==b,prefix=actual is not None and len(actual)<len(b) and b.startswith(actual),
            sha256=None if actual is None else digest(actual),launcher_absent=launcher_absent,
            verified_files=sum(x['kind']=='write_verified' for x in rows),console_writes=False,console_c_accessed=False)
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
