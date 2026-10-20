"""Pinned original NT5 subject, qualified-core recorder and counter observer."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn619/build002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
out=K/'build002.json';assert not out.exists()
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
r=dict(status='building',compiler_sha256=sha(cc),space=require_space('/mnt/c',20.02),physical_access=False,commands=[],rows=[],headers={})
O.mkdir(parents=True)
for p in list(K.glob('*.c'))+list(K.glob('*.h'))+list(K.glob('*.S')):shutil.copyfile(p,O/p.name)
def save():out.write_text(json.dumps(r,indent=2)+'\n')
try:
 for src,name in [('subject.c','subject.exe'),('runner.c','run619.exe')]:
  cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin',
   '-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',name+'.d','-o',name,src,
   '-lkernel32','-luser32','-ladvapi32','-lgdi32']
  if src=='subject.c':
   acmd=[str(cc),'-c','ranges.S','-o','ranges.o'];r['commands'].append(acmd)
   subprocess.run(acmd,cwd=O,check=True,timeout=30)
   cmd.append('ranges.o')
  r['commands'].append(cmd);save()
  with (O/(name+'.log')).open('wb') as log:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,timeout=180,check=True)
  deps=(O/(name+'.d')).read_text().replace('\\\n','').split(': ',1)[1].split()
  r['headers'].update({n:sha(n) for n in set(deps) if Path(n).is_absolute()})
  pe=pefile.PE(str(O/name));assert pe.FILE_HEADER.Machine==0x14c
  imports={d.dll.decode():[v.name.decode() for v in d.imports] for d in pe.DIRECTORY_ENTRY_IMPORT}
  assert all(n.lower() in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll'] for n in imports)
  r['rows'].append(dict(path=str(O/name),bytes=(O/name).stat().st_size,sha256=sha(O/name),imports=imports))
 r['status']='compiled'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
if r['status']=='compiled':
 (K/'binary-review001.json').write_text(json.dumps(dict(passed=True,build_sha256=sha(out),
  scope='PE32 i386, NT5 subsystem, allowed OS imports and original assembly source ranges.'),indent=2)+'\n')
