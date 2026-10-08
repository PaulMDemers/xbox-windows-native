"""Check every actual bounded step retry and its subsequent observed progress."""
import json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';dest=k/'step-verification.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();t=json.loads((out/'trace.json').read_text());steps=t['single_steps'];retries=[]
for i,s in enumerate(steps):
 unchanged=s['before']==s['after'] and s['before_owner']==s['after_owner']
 assert unchanged==s['unchanged'] and 0<=s['attempt']<4 and s['before']['EIP'] not in s['armed'] and s['reply'].startswith(('T','S'))
 if s['attempt']:
  prev=steps[i-1];assert prev['unchanged'] and s['attempt']==prev['attempt']+1 and s['before']==prev['after'] and s['before_owner']==prev['after_owner']
 if unchanged:
  assert i+1<len(steps) and steps[i+1]['attempt']==s['attempt']+1
  retries.append(dict(index=i,eip=s['before']['EIP'],attempt=s['attempt'],next_eip=steps[i+1]['after']['EIP'],next_unchanged=steps[i+1]['unchanged']))
 else:
  if i+1<len(steps):assert steps[i+1]['attempt']==0
assert not steps[-1]['unchanged'] and t['status']=='104_snapshots_pending_cold_oracle'
r=dict(passed=True,steps=len(steps),no_progress_replies=len(retries),retries=retries,trace_sha256=sha(out/'trace.json'),verifier_sha256=sha(Path(__file__)),limits='Real bounded stepping without marker deduplication or guest register/code writes; underlying reason for no-progress stop remains unresolved.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Verified',len(steps),'steps and',len(retries),'bounded no-progress retries')
