"""Review frozen inputs and exact staged public bytes without reopening runtime."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'staged-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda n:Path(n.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=dict(passed=False)
try:
 final=read('final001.json');assert final['closed'] and final['passed']
 for n,h in final['pins'].items():assert sha(K/n)==h,n
 for n,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(host(n))==h,n
 for n,v in read('build001.json')['files'].items():
  p=host(n);assert sha(p)==v['sha256'],n
  if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes(),n
 for p in K.glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
 rows={}
 for n in subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines():
  assert n.startswith('outputs/rct609/') or n in ['docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],n
  p=W/n;assert p.suffix in ['.py','.json','.c','.h','.md'] or p.name=='.gitattributes'
  assert subprocess.check_output(['git','show',':'+n],cwd=W)==p.read_bytes(),n
  rows[n]=dict(bytes=p.stat().st_size,sha256=sha(p))
 r.update(passed=True,staged=rows)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('609 exact frozen and staged bytes passed:',len(rows))
