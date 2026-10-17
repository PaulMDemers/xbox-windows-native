"""Build one unique read-only inventory XBE with prebuilt shared SDK libraries."""
import datetime, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
k = Path(__file__).resolve().parent
attempt = sys.argv[1]
assert re.fullmatch(r'\d{3}', attempt)
out = Path('C:/xwn434') / ('build' + attempt)
record = k / ('build' + attempt + '.json')
assert not out.exists() and not record.exists()
assert shutil.disk_usage('C:/').free - 192*1024**2 >= 20*1024**3
assert shutil.disk_usage('E:/').free >= 20*1024**3
sdk = Path('C:/nxdk')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def pins():
    paths = list((sdk/'lib').rglob('*.lib')) + list((sdk/'lib').rglob('*.h'))
    paths += [sdk/'Makefile', sdk/'lib/hal/video.c', sdk/'lib/hal/xbox.c']
    paths += list((sdk/'bin').glob('nxdk-*'))
    paths += [sdk/'tools/cxbe/cxbe.exe', sdk/'tools/extract-xiso/build/extract-xiso.exe']
    return {str(p.relative_to(sdk)): sha(p) for p in paths if p.is_file()}
before = pins()
expected = json.loads((k.parent/'owned-texture271/build005.json').read_text())['sdk_before']
for name in ['lib\\libnxdk_hal.lib', 'lib\\libnxdk.lib', 'lib\\libwinapi.lib', 'lib\\xboxkrnl\\libxboxkrnl.lib']:
    assert before[name] == expected[name], name
out.mkdir(parents=True)
(out/'input').mkdir()
for name in ['main.c', 'pattern.h', 'Makefile', 'Build.ps1', 'build.py']:
    shutil.copyfile(k/name, out/'input'/name)
for name in ['main.c', 'pattern.h', 'Makefile']: shutil.copyfile(k/name, out/name)
r = dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), output=str(out),
         source={p.name:sha(p) for p in (out/'input').iterdir()}, sdk_before=before,
         compiled=False, physical_access=False, guest_launched=False)
def run(command, label):
    p = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        'C:/Homebrew/Invoke-Console.ps1', '-Console', 'xbox', '-WorkingDirectory', str(out),
        '-Command', command], capture_output=True, timeout=180)
    data = p.stdout + p.stderr
    (out/label).write_bytes(data)
    (k/('build'+attempt+'-'+label)).write_bytes(data)
    assert p.returncode == 0, data.decode(errors='replace')[-3000:]
    return data.decode(errors='replace')
try:
    plan = run('make -n V=1', 'plan.log')
    assert not re.search(r'\[ (?:LIB|AS|BUILD|CXX)\s+\]', plan), 'Shared SDK rebuild refused'
    commands = [s.strip() for s in plan.splitlines() if s.strip().startswith(('nxdk-cc ', 'nxdk-link ', 'make ', '/c/nxdk/'))]
    assert sum(s.startswith('nxdk-cc ') for s in commands) == 1
    for s in commands:
        assert not s.startswith('make '), s
        if s.startswith('nxdk-cc '): assert "-o '/c/xwn434/build"+attempt+"/main.obj'" in s
        if s.startswith('/c/nxdk/'):
            assert any(t in s for t in ['/cxbe/cxbe ', '/extract-xiso/build/extract-xiso ']), s
    r['preflight_commands'] = commands
    log = run('make -j4 V=1', 'compile.log')
    warnings = [s for s in log.splitlines() if re.search(r'\bwarning:', s, re.I)]
    assert warnings == ['lld: warning: .edata=.rdata: already merged into .edataxb'], warnings
    r['reviewed_warning'] = 'Pinned nxdk export-section merge warning; no suppression.'
    r['outputs'] = {n:dict(bytes=(out/n).stat().st_size,sha256=sha(out/n)) for n in
                    ['main.exe','main.map','main.c.d','bin/default.xbe','hd434.iso']}
    headers = sorted(set(re.findall(r'C:/nxdk/[^\s:]+', (out/'main.c.d').read_text())))
    r['used_headers'] = {n:sha(Path(n)) for n in headers}
    for n in headers: assert before[str(Path(n).relative_to(sdk))] == sha(Path(n))
    r['compiled'] = True
except Exception as e:
    r['failure'] = repr(e)
finally:
    r['sdk_after'] = pins(); r['sdk_unchanged'] = before == r['sdk_after']
    r['closed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r.get(n) for n in ['compiled','sdk_unchanged','failure','output']},indent=2))
assert r['compiled'] and r['sdk_unchanged']
