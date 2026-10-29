"""Read-only reconciliation of the uncertain805 STOR reply; never resend."""
from pathlib import Path
import json,datetime,hashlib
from physical import connect,names,get,verify,REMOTE
K=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
out=K/'stage-reconcile001.json';assert not out.exists()
r={'passed':False,'console_writes':False,'launch_sent':False,'source_sha256':sha(Path(__file__).read_bytes())}
try:
 data=verify();s=json.loads((K/'stage001.json').read_text());assert not s['completed'] and s['failure_type']=='TimeoutError'
 assert s['writes']==[REMOTE,REMOTE+'/owner.json',REMOTE+'/default.xbe']
 with connect() as f:
  r['entries']=names(f,REMOTE);assert set(r['entries'])=={'owner.json','default.xbe'}
  owner=get(f,REMOTE+'/owner.json');assert sha(owner)==s['staged'][REMOTE+'/owner.json']['sha256']
  assert json.loads(owner)['xbe_sha256']==sha(data)
  actual=get(f,REMOTE+'/default.xbe');assert actual==data
  r['staged']={REMOTE+'/owner.json':{'bytes':len(owner),'sha256':sha(owner)},REMOTE+'/default.xbe':{'bytes':len(actual),'sha256':sha(actual)}}
  assert not any(n.lower().startswith('xwn-mode805-') for n in names(f,'/E'))
 r['passed']=True
except BaseException as e:r['failure_type']=type(e).__name__;raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS805 exact staged bytes reconciled read-only; no launch')
