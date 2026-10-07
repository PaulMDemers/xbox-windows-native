"""Verify immutable inputs, actual-source host tests and all three closed guests."""
import ast,datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];diag=k.parent/'video-ownership-scanout'
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
rows=[]
for kit,case in [(k,'control001'),(k,'candidate001'),(diag,'candidate001')]:
 out=kit/case;c=read(out/'closure.json');f=read(kit/('fixture-'+case+'.json'));p=read(out/'preflight.json');a=read(out/'audit.json')
 assert sha(Path(c['private_disk']))==c['private_disk_sha256']
 for name,h in p['sources'].items():assert sha(out/'source'/name)==h
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 for v in f['parents']:assert sha(host(v['path']))==v['sha256']
 assert a['debugger']==(kit==diag) and a['strict_qualification_passed']
 rows.append(dict(kit=kit.name,case=case,closed=True,debugger=a['debugger'],cold_strict_pass=True,snapshot_files=len(p['sources']),closure_sha256=sha(out/'closure.json')))
for kit in [k,diag]:
 for p in kit.glob('*.py'):ast.parse(p.read_text())
 for name,h in read(kit/'patch-review.json')['source_files'].items():assert sha(kit/'display'/name)==h
 for name in ['host-tests.json','ownership-tests.json','lifecycle-tests.json']:
  test=read(kit/name);assert test['passed']
  for p,h in test['pins'].items():assert sha(kit/p)==h
assert read(k/'pair-review.json')['passed'] and read(diag/'verification.json')['passed']
assert not read(diag/'verification.json')['ordinary_qualified']
dest=k/'evidence-verification.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,closed_cases=rows,verifier_sha256=sha(Path(__file__))),indent=2)+'\n')
print('Host source pins, immutable inputs and three closed ordinary/diagnostic guests verified')
