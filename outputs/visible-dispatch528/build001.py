"""One unique pinned nxdk build; no shared SDK compilation allowed."""
import hashlib, json, pathlib, re, shutil, subprocess, sys
K = pathlib.Path(__file__).resolve().parent
R = K.parent.parent
out = pathlib.Path('C:/xwn528/build001')
assert not out.exists() and not (K/'build001.json').exists()
assert all(shutil.disk_usage(d).free - 64*1024**2 >= 20*1024**3 for d in ['C:/'])
sdk = pathlib.Path('C:/nxdk')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert all(json.loads((K/n).read_text())['passed'] for n in ['host001.json','ui-host001.json','controller-host001.json','supervisor-host001.json'])
head = subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD']).decode().strip()
assert head == '58427c078b4ccb0121f359b6b6c536b3b2914976'
def pins():
    paths = list(sdk.rglob('*.lib')) + list(sdk.rglob('*.h')) + list((sdk/'bin').glob('nxdk-*'))
    paths += [sdk/n for n in ['lib/hal/video.c','lib/hal/debug.c','lib/nxdk/mount.c','lib/nxdk/automount_d.c']]
    paths += [sdk/'Makefile', sdk/'tools/cxbe/cxbe.exe', sdk/'tools/extract-xiso/build/extract-xiso.exe']
    return {str(p.relative_to(sdk)):sha(p) for p in paths if p.is_file()}
ui=json.loads((K/'ui-host001.json').read_text())
for n,h in ui['source_sha256'].items(): assert sha(K/n)==h
before = pins()
(K/'prebuild001.json').write_text(json.dumps(dict(sdk_head=head,sdk=before,sources={n:sha(K/n) for n in ['main.c','engine.c','engine.h','Makefile']},tools={str(p):sha(p) for p in [pathlib.Path('C:/Homebrew/Invoke-Console.ps1'),pathlib.Path('C:/Homebrew/console-env.sh'),pathlib.Path('C:/msys64/mingw64/bin/clang.exe'),pathlib.Path('C:/msys64/mingw64/bin/lld.exe'),pathlib.Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1')]}),indent=2)+'\n')
out.mkdir(parents=True)
for name in ['main.c','engine.c','engine.h','Makefile']:
    shutil.copy2(K/name,out/name)
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
    plan=make('make -n V=1','build001-plan.log')
    assert not re.search(r'\[ (?:LIB|AS|BUILD|CXX)\s+\]',plan)
    assert plan.count("nxdk-cc ")==2
    assert all("-o '/c/xwn528/build001/"+n+".obj'" in plan for n in ['main','engine'])
    log=make('make -j2 V=1','build001-compile.log')
    warnings=[x for x in log.splitlines() if 'warning:' in x]
    assert warnings==['lld: warning: .edata=.rdata: already merged into .edataxb'],warnings
    r['warnings']=warnings
    r['outputs']={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in out.rglob('*') if p.is_file()}
    r['compiled']=True
except Exception as e:
    r['failure']=repr(e);r['compiled']=False
finally:
    r['sdk_unchanged']=pins()==before
    (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ('sdk_before','outputs')}))
assert r['compiled'] and r['sdk_unchanged']
