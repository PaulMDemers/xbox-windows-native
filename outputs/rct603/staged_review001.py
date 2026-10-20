"""Exact source and evidence/index review; no new guest activity."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
def host(n):return Path(n.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
out=K/'staged-review001.json';assert not out.exists();r=dict(passed=False)
try:
 final=read('final001.json');assert final['closed'] and final['passed']
 for name,h in final['pins'].items():assert sha(K/name)==h,name
 for name,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(host(name))==h,name
 for build in ['build001.json','build002.json']:
  b=read(build)
  for name,v in b['files'].items():
   p=host(name);assert sha(p)==v['sha256'],name
   if p.suffix in ['.c','.h']:assert p.read_bytes()==(K/p.name).read_bytes(),name
 assert read('build001.json')['status']=='failed' and read('build002.json')['status']=='compiled'
 for n in ['review001.json','scene-review001.json','visual-review001.json','scene-tests001.json','source-review002.json','binary-review001.json','asset-header-review001.json','media-review001.json','setup-review001.json']:assert read(n)['passed']
 for p in K.glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
 names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines();rows={}
 for name in names:
  assert name.startswith('outputs/rct603/') or name in ['docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],name
  p=W/name;assert '__pycache__' not in p.parts and (p.suffix in ['.md','.py','.json','.c','.h'] or p.name=='.gitattributes')
  data=subprocess.check_output(['git','show',':'+name],cwd=W);assert data==p.read_bytes(),name
  rows[name]=dict(bytes=len(data),sha256=sha(p))
 r.update(passed=True,staged=rows,scope='Frozen preparation/build001 failure/build002/closure sources and exact public index bytes. No runtime reopening.')
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('603 frozen sources and exact staged bytes passed:',len(rows))
