"""Review frozen source/build/runtime pins and exact public staged bytes."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'staged-review002.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
r=dict(passed=False)
try:
 f=read('final001.json');assert f['closed'] and f['passed'] and f['cleanup_passed']
 for n,h in f['pins'].items():assert sha(K/n)==h,n
 for path,h in read('ntfs-preparation001.json')['inputs'].items():assert sha(host(path))==h,path
 for path,v in read('build002.json')['files'].items():
  p=host(path);assert sha(p)==v['sha256']
  if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes()
 for p in K.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
 names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines()
 expected={str(p.relative_to(W)).replace(chr(92),'/') for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.json','.c','.h','.md'] or p.name=='.gitattributes')}
 expected.update(['docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'])
 assert len(expected)>50 and set(names)==expected,(set(names)^expected)
 rows={}
 for n in subprocess.check_output(['git','diff','--cached','--name-only'],cwd=W,text=True).splitlines():
  assert n.startswith('outputs/rct616/') or n in ['docs/rct-performance-plan.md',
   'outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],n
  p=W/n;assert p.suffix in ['.py','.json','.c','.h','.md'] or p.name=='.gitattributes'
  assert subprocess.check_output(['git','show',':'+n],cwd=W)==p.read_bytes(),n
  rows[n]=dict(bytes=p.stat().st_size,sha256=sha(p))
 r.update(passed=True,staged=rows)
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('Exact staged bytes passed',len(rows))
