"""Check frozen601/602 evidence and exact index bytes; no guest access."""
import hashlib,json,subprocess
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
out=K/'staged-review001.json';assert not out.exists()
result=dict(passed=False,checks={},scope='Frozen source/build/preparation/closure pins and exact staged public bytes; no new runtime or recollection.')
try:
 for number,build in [(601,'build002.json'),(602,'build001.json')]:
  root=W/'outputs'/('rct'+str(number));final=read(root/'final001.json');prep=read(root/'ntfs-preparation001.json')
  assert final['closed'] and final['passed']
  for name,h in prep['inputs'].items():assert sha(host(name))==h,name
  for name,row in read(root/build)['files'].items():
   p=host(name);assert sha(p)==row['sha256'],name
   if p.suffix in ['.c','.h'] and (root/p.name).exists():assert p.read_bytes()==(root/p.name).read_bytes(),name
  for name,h in final['pins'].items():assert sha(root/name)==h,(number,name)
  for p in root.glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
  for p in root.glob('*.json'):read(p)
  state=read(root/'ntfs-phase1.json');assert state['closed'] and state['exit_code']==0
  assert not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
  result['checks'][str(number)]='Frozen pins, closed VM, Python syntax and JSON passed'
 checks={'601':['review002.json','event-review001.json','oracle-tests001.json','host-tests001.json','binary-review001.json','media-review001.json'],
 '602':['review001.json','drawing-review001.json','visual-review001.json','recorder-review001.json','binary-review001.json','media-review001.json']}
 for number,names in checks.items():
  for name in names:assert read(W/'outputs'/('rct'+number)/name)['passed']
 names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines();rows={}
 allowed={'docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'}
 for name in names:
  p=W/name;assert name in allowed or name.startswith(('outputs/rct601/','outputs/rct602/')),name
  assert '__pycache__' not in p.parts and (p.suffix in ['.py','.json','.c','.h','.md'] or p.name=='.gitattributes'),name
  data=subprocess.check_output(['git','show',':'+name],cwd=W);assert data==p.read_bytes(),name
  rows[name]=dict(bytes=len(data),sha256=sha(p))
 result.update(passed=True,staged=rows)
except BaseException as e:result['error']=repr(e);raise
finally:out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('601/602 frozen pins and exact staged bytes passed:',len(rows))
