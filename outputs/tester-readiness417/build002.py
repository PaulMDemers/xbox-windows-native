"""One unique pinned nxdk build; no shared SDK compilation allowed."""
import hashlib, json, pathlib, re, shutil, subprocess, sys
K = pathlib.Path(__file__).resolve().parent
R = K.parent.parent
out = pathlib.Path('E:/xwn417/build002')
assert not out.exists() and not (K/'build002.json').exists()
assert all(shutil.disk_usage(d).free - 64*1024**2 >= 20*1024**3 for d in ['C:/','E:/'])
sdk = pathlib.Path('C:/nxdk')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD']).decode().strip()
assert head == '58427c078b4ccb0121f359b6b6c536b3b2914976'
def pins():
    paths = list(sdk.rglob('*.lib')) + list(sdk.rglob('*.h')) + list((sdk/'bin').glob('nxdk-*'))
    paths += [sdk/'Makefile', sdk/'tools/cxbe/cxbe.exe', sdk/'tools/extract-xiso/build/extract-xiso.exe']
    return {str(p.relative_to(sdk)):sha(p) for p in paths if p.is_file()}
before = pins()
out.mkdir(parents=True)
for p in (R/'src/utilities/hardware-report').iterdir():
    if p.is_file(): shutil.copy2(p,out/p.name)
r = dict(sdk_head=head, sources={p.name:sha(p) for p in out.iterdir()}, sdk_before=before,
         guest_launched=False, physical_access=False, output=str(out))
def make(command, log):
    p = subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',
        'C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(out),'-Command',command],
        capture_output=True,timeout=180)
    data=p.stdout+p.stderr; (K/log).write_bytes(data)
    assert p.returncode==0,data.decode(errors='replace')[-2500:]
    return data.decode(errors='replace')
try:
    plan=make('make -n V=1','build002-plan.log')
    assert not re.search(r'\[ (?:LIB|AS|BUILD|CXX)\s+\]',plan)
    assert plan.count("nxdk-cc ")==1
    assert "-o '/e/xwn417/build002/main.obj'" in plan
    log=make('make -j2 V=1','build002-compile.log')
    warnings=[x for x in log.splitlines() if 'warning:' in x]
    assert warnings==['lld: warning: .edata=.rdata: already merged into .edataxb'],warnings
    r['warnings']=warnings
    r['outputs']={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in out.rglob('*') if p.is_file()}
    r['compiled']=True
except Exception as e:
    r['failure']=repr(e);r['compiled']=False
finally:
    r['sdk_unchanged']=pins()==before
    (K/'build002.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ('sdk_before','outputs')}))
assert r['compiled'] and r['sdk_unchanged']
