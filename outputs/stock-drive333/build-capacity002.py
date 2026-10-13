"""Unique prebuilt-SDK capacity probe build; no physical access or guest launch."""
import hashlib,json,pathlib,re,shutil,subprocess
K=pathlib.Path(__file__).resolve().parent;out=pathlib.Path('E:/xwn333/capacity-build002')
report=K/'capacity-build002.json';assert not out.exists() and not report.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>20*1024**3
assert shutil.disk_usage('E:/').free-256*1024**2>20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sdk=pathlib.Path('C:/nxdk');out.mkdir(parents=True)
for name in ['capacity002.c','Makefile']:shutil.copyfile(K/name,out/('capacity.c' if name=='capacity002.c' else name))
paths=[p for p in sdk.rglob('*') if p.is_file() and (p.suffix in ['.lib','.h'] or p.parent==sdk/'bin')]
before={str(p.relative_to(sdk)):sha(p) for p in paths}
r=dict(source={n:sha(K/n) for n in ['capacity002.c','Makefile','build-capacity002.py']},sdk_before=before,physical_access=False,guest_launch=False)
def run(command,label):
    p=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(out),'-Command',command],capture_output=True,timeout=180)
    b=p.stdout+p.stderr;(out/label).write_bytes(b)
    assert p.returncode==0,b[-2500:].decode(errors='replace')
    return b.decode(errors='replace')
try:
    plan=run('make -n V=1','plan.log')
    assert not re.search(r'\[ (?:LIB|AS|BUILD|CXX)\s+\]',plan)
    assert not any(x.strip().startswith('make ') for x in plan.splitlines())
    log=run('make -j4 V=1','build.log')
    warnings=[x for x in log.splitlines() if re.search(r'\bwarning:',x,re.I)]
    assert warnings==['lld: warning: .edata=.rdata: already merged into .edataxb'],warnings
    r.update(compiled=True,warnings=warnings,outputs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in [out/'bin/default.xbe',out/'capacity333.iso',out/'capacity.map']})
except Exception as e:r.update(compiled=False,error=repr(e));raise
finally:
    r['sdk_unchanged']=all(sha(sdk/n)==h for n,h in before.items());report.write_text(json.dumps(r,indent=2)+'\n')
assert r['sdk_unchanged'];print('Capacity probe compiled; SDK unchanged')
