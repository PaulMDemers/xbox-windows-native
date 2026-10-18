"""Compile namespace-only runner with pre/post header, tool and archive closure."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn501/runner-build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
out=K/'runner-build001.json';assert not out.exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>=20*1024**3
source=(K/'runner.c').read_text();original=(K.parent/'d3d-scene496/runner.c').read_text()
assert source.replace('501','496').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('C:'+chr(92)*2+'xwn496-kit'+chr(92)*2+'d3d.exe','A:'+chr(92)*2+'D3D.EXE')==original
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
O.mkdir(parents=True);shutil.copyfile(K/'runner.c',O/'runner.c')
r=dict(status='preflight',physical_access=False,source_namespace_only=True,compiler_sha256=sha(cc))
def save():out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(args):return subprocess.check_output(args,cwd=O,text=True,timeout=30).strip()
save()
try:
 headers=run([str(cc),'-M','runner.c']).replace('\\\n','').split(': ',1)[1].split()
 paths={K/'runner.c',Path(__file__),cc,*[Path(n) for n in headers if Path(n).is_absolute()]}
 tools=[cc]
 for name in ['cc1','as','ld','collect2']:
  p=Path(run([str(cc),'-print-prog-name='+name]));p=p if p.is_absolute() else Path(shutil.which(str(p)));assert p.is_file();tools.append(p);paths.add(p)
 for name in ['libkernel32.a','libuser32.a','libadvapi32.a','libgcc.a']:
  p=Path(run([str(cc),'-print-file-name='+name]));assert p.is_file();paths.add(p)
 for tool in tools:
  q=subprocess.run(['ldd',str(tool)],capture_output=True,text=True,timeout=30)
  for name in re.findall(r'(/[^\s()]+)',q.stdout):
   p=Path(name)
   if p.is_file():paths.add(p)
 sample=Path('/home/paul/xbox-windows-native/d3d-scene496-runner-build001/d3d.exe')
 assert sha(sample)=='7cbf053f41ef256e812cc732a306679a21b2a5087920541474fc71d133c85c64';paths.add(sample)
 r['prebuild_inputs']={str(p):sha(p) for p in sorted(paths)}
 r['status']='building';save()
 cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF','headers.d','-o','run501.exe','runner.c','-lkernel32','-luser32','-ladvapi32']
 with (O/'build.log').open('xb') as log:subprocess.run(cmd,cwd=O,check=True,stdout=log,stderr=log,timeout=180)
 assert all(sha(Path(n))==h for n,h in r['prebuild_inputs'].items())
 actual=(O/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split()
 assert {n for n in actual if Path(n).is_absolute()}<={str(p) for p in paths}
 shutil.copyfile(sample,O/'d3d.exe')
 r.update(status='compiled',exit_code=0,command=cmd,prebuild_inputs_unchanged=True,rows=[dict(path=str(O/n),sha256=sha(O/n),bytes=(O/n).stat().st_size) for n in ['run501.exe','d3d.exe']])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
