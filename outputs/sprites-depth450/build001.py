"""Compile the owned guest controller; never execute it on the host."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/sprites-depth450-runner-build001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not (K/'build001.json').exists()
space=require_space(P,20+8/1024)
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
P.mkdir();shutil.copyfile(K/'runner.c',P/'runner.c')
cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',str(P/'headers.d'),'-o',str(P/'run450.exe'),str(P/'runner.c'),'-lkernel32','-luser32','-ladvapi32']
record=dict(command=cmd,space=space,compiler_sha256=sha(cc),source_sha256=sha(P/'runner.c'),host_execution=False,rows=[])
with (P/'build.log').open('xb') as f:ret=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
record.update(exit_code=ret,log_sha256=sha(P/'build.log'))
if ret==0:
 deps=(P/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split()
 record['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/'runner.c'}
 for p in [P/'run450.exe',Path('/home/paul/xbox-windows-native/sprites444-build001/sprites.exe')]:record['rows'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
(K/'build001.json').write_text(json.dumps(record,indent=2)+'\n')
assert ret==0,(P/'build.log').read_text()
assert record['rows'][1]['sha256']=='23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f'
print('Controller compiled; sample unchanged; neither executed on host.')
