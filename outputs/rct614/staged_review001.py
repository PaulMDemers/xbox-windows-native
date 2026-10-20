"""Verify both closed outcomes and every staged byte; no runtime recollection."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'staged-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
r=dict(passed=False)
try:
 for n,passed,build in [(613,False,'build002.json'),(614,True,'build001.json')]:
  root=K.parent/f'rct{n}'
  read=lambda p:json.loads((root/p).read_text(encoding='utf-8'))
  f=read('final001.json')
  assert f['closed'] and f['passed']==passed and f['cleanup_passed']
  for name,h in f['pins'].items():assert sha(root/name)==h,name
  for path,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(host(path))==h,path
  for path,row in read(build)['files'].items():
   p=host(path);assert sha(p)==row['sha256']
   if p.suffix=='.c':assert p.read_bytes()==(root/p.name).read_bytes()
  for p in root.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
 rows={}
 for n in subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines():
  assert n.startswith(('outputs/rct613/','outputs/rct614/')) or n in [
   'docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],n
  p=W/n;assert p.suffix in ['.py','.json','.c','.h','.md'] or p.name=='.gitattributes'
  assert subprocess.check_output(['git','show',':'+n],cwd=W)==p.read_bytes(),n
  rows[n]=dict(bytes=p.stat().st_size,sha256=sha(p))
 r.update(passed=True,staged=rows,closed_outcomes={'613':'failed qualification / cleanup passed','614':'passed control / cleanup passed'})
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('Exact staged review passed:',len(rows))
