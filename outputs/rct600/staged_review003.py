from pathlib import Path
import hashlib,json,subprocess
k=Path('outputs/rct600')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
def read(n):return json.loads((k/n).read_text())
prep=read('ntfs-preparation001.json');b=read('build001.json');final=read('final001.json')
assert final['closed'] and final['passed']
for name,h in prep['inputs'].items():assert sha(host(name))==h,name
for name,row in b['files'].items():
 p=host(name);assert sha(p)==row['sha256'],name
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(k/p.name).read_bytes(),name
for name,h in final['inputs'].items():assert sha(Path(name))==h,name
for p in k.glob('*.py'):compile(p.read_text(),str(p),'exec')
for n in ['host-tests001.json','oracle-tests001.json','binary-review001.json','media-review001.json','trace-review001.json']:assert read(n)['passed']
assert not read('ntfs-phase1.json').get('capture_errors')
names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
rows={}
for name in names:
 assert name.startswith('outputs/rct600/') or name in ['docs/rct-performance-plan.md','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],name
 p=Path(name);assert '__pycache__' not in p.parts and p.suffix!='.pyc';data=subprocess.check_output(['git','show',':'+name]);assert data==p.read_bytes(),name
 rows[name]=dict(bytes=len(data),sha256=sha(p))
out=k/'staged-review003.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,staged=rows,scope='Exact frozen prep/build/closure pins, Python syntax and index bytes; no new runtime.'),indent=2)+'\n')
print('600 pins and exact staged bytes checked:',len(rows))
