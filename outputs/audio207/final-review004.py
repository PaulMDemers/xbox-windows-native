"""Final immutable-input, source syntax, closure and package review."""
import ast,hashlib,json,pathlib,subprocess
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
parsed=[]
for p in sorted(k.glob('*.py')):ast.parse(p.read_text(encoding='utf-8-sig'));parsed.append(p.name)
frozen={};staged=set()
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=repo).decode().strip('\0').split('\0'))
for p in sorted(k.glob('frozen*.json')):
    pins=json.loads(p.read_text());frozen[p.name]=len(pins)
    for n,h in pins.items():
        assert sha(repo/n)==h,(p.name,n)
        if n in tracked:
            b=subprocess.check_output(['git','show',':'+n],cwd=repo)
            assert hashlib.sha256(b).hexdigest()==h,('Staged bytes mismatch',n)
            staged.add(n)
for case,field in [('candidate004','scoped_audio_passed'),('install001','scoped_installation_passed'),('installed001','scoped_audio_passed'),('installed002','scoped_audio_passed')]:
    audit=k/case/'audit.json';closure=json.loads((k/case/'closure.json').read_text())
    assert closure['closed'] and closure['audit_sha256']==sha(audit)
    assert json.loads(audit.read_text())[field]
    assert json.loads(audit.read_text())['strict_qualification_passed'] is False
for p in json.loads((k/'package001.json').read_text())['packages']:
    assert sha(pathlib.Path(p['delivered_path']))==p['sha256']
    assert sha(k/'artifacts/hardware-package001'/p['name'])==p['sha256']
logs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(k.glob('*.log')) if not p.name.startswith(('push-','final-review'))}
dest=k/'host-log-pins002.json';assert not dest.exists();dest.write_text(json.dumps(logs,indent=2)+'\n')
r=dict(passed=True,python_sources_parsed=parsed,frozen_manifests=frozen,staged_frozen_files_verified=len(staged),closed_qualification_cases=4,delivered_packages_readback_verified=2)
dest=k/'static-review004.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({x:y for x,y in r.items() if x!='python_sources_parsed'},indent=2))
