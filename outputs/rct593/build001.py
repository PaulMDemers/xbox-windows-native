"""Build frozen NT5 input runner and independent prelaunch asset verifier."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn593/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
from asset_header_check001 import validate
assert validate((K/'assets.h').read_text(),json.loads((K/'asset-integrity001.json').read_text()))
assert not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-16*1024**2>=20*1024**3
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
O.mkdir(parents=True)
for f in list(K.glob('*.c'))+list(K.glob('*.h')):shutil.copyfile(f,O/f.name)
r=dict(status='building',compiler_sha256=sha(cc),physical_access=False,commands=[],headers={},rows=[])
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for src,exe in [('runner.c','run593.exe'),('verify.c','verify593.exe')]:
  cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',exe+'.d','-o',exe,src,'-lkernel32','-luser32','-ladvapi32','-lgdi32']
  r['commands'].append(cmd)
  with (O/(exe+'.log')).open('wb') as log:subprocess.run(cmd,cwd=O,check=True,stdout=log,stderr=log,timeout=180)
  deps=(O/(exe+'.d')).read_text().replace('\\\n','').split(': ',1)[1].split()
  r['headers'].update({n:sha(Path(n)) for n in sorted(set(deps)) if Path(n).is_absolute()})
  r['rows'].append(dict(path=str(O/exe),sha256=sha(O/exe),bytes=(O/exe).stat().st_size))
 r.update(status='compiled',exit_code=0)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
