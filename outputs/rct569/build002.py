"""Build bounded RCT control runner; no game binary modification."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn569/runner-build002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
assert not (K/'runner-build002.json').exists()
assert shutil.disk_usage('/mnt/c').free-16*1024**2>=20*1024**3
source=(K/'runner.c').read_text()
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
O.mkdir(parents=True);shutil.copyfile(K/'runner.c',O/'runner.c');shutil.copyfile(K/'input.h',O/'input.h')
r=dict(status='building',source_namespace_only=False,compiler_sha256=sha(cc),physical_access=False)
def save():(K/'runner-build002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF','headers.d','-o','run569.exe','runner.c','-lkernel32','-luser32','-ladvapi32','-lgdi32']
 with (O/'build.log').open('wb') as log:subprocess.run(cmd,cwd=O,check=True,stdout=log,stderr=log,timeout=180)
 deps=(O/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split()
 r.update(status='compiled',exit_code=0,command=cmd,headers={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n).is_absolute()},rows=[dict(path=str(O/n),sha256=sha(O/n),bytes=(O/n).stat().st_size) for n in ['run569.exe']])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
