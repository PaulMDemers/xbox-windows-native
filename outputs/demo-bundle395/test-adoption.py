"""Actual adoption transaction with modeled transport and journal; no console access."""
import ast, copy, hashlib, json
from pathlib import Path
K=Path(__file__).resolve().parent
source=(K/'adopt.py').read_bytes()
tree=ast.parse(source)
body=[n for n in tree.body if isinstance(n,ast.With)]
assert len(body)==1
code=compile(ast.Module(body=body,type_ignores=[]),str(K/'adopt.py'),'exec')
sha=lambda b:hashlib.sha256(b).hexdigest()
driver='/E/winnt/system32/drivers/xwnfatx.sys'
normal=b'original';candidate=b'candidate';protected='/E/protected'
results=[]
for scenario in ['success','baseline_changed','partial_write','candidate_readback',
                 'protected_after_write','rollback_failure']:
 files={driver:normal,protected:b'unchanged'};writes=[];journal=[]
 state={'accepted':False,'write_requested':False};stage=[0]
 class Connection:
  def __enter__(self):return self
  def __exit__(self,*args):return False
 def fetch(ftp,path):
  if scenario=='baseline_changed' and path==protected and not stage[0]:return b'changed'
  if scenario=='candidate_readback' and stage[0]==1 and path==driver:return b'bad'
  if scenario=='protected_after_write' and stage[0]==1 and path==protected:return b'changed'
  return files[path]
 def store(ftp,path,data,case):
  assert path==driver and case=='candidate001';writes.append(data);stage[0]+=1
  if scenario in ['partial_write','rollback_failure'] and stage[0]==1:
   files[path]=data[:2];raise OSError('modeled partial transfer')
  if scenario=='rollback_failure' and stage[0]==2:raise OSError('modeled rollback failure')
  files[path]=data
 env=dict(connect=Connection,fetch=fetch,store=store,FATX=driver,CANDIDATE=sha(candidate),
          candidate=candidate,original=normal,case='candidate001',sha=sha,
          f={'files':{p:{'sha256':sha(b)} for p,b in files.items()}},r=state,
          dest=None,write_json=lambda dest,r:journal.append(copy.deepcopy(r)),utc=lambda:'modeled')
 failed=False
 try:exec(code,env)
 except (AssertionError,OSError):failed=True
 if scenario=='success':
  assert not failed and state['accepted'] and files[driver]==candidate and writes==[candidate]
 elif scenario=='baseline_changed':
  assert failed and not state['accepted'] and not writes and not state['write_requested']
 else:
  assert failed and not state['accepted'] and writes==[candidate,normal]
  assert state['original_restored_after_failure']==(scenario!='rollback_failure')
  if scenario=='rollback_failure':assert 'rollback_error' in state
  else:assert files[driver]==normal
 assert all(not row.get('accepted') for row in journal[:-1])
 results.append(dict(scenario=scenario,failed=failed,accepted=state['accepted'],
                     write_count=len(writes),rollback_confirmed=state.get('original_restored_after_failure')))
out=K/'adoption-host001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,scope='Actual with-connect orchestration; FTP/store/journal modeled. Actual bounded store separately tested by physical394. No hardware access.',source_sha256=sha(source),cases=results),indent=2)+'\n')
print('Six adoption transaction cases passed; no hardware access')
