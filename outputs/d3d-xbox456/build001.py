"""Compile fresh physical controller; reuse exact qualified d3d-discovery455 sample."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/home/paul/xbox-windows-native/d3d-xbox456-runner-build001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not (K/'build001.json').exists()
assert json.loads((K.parent/'d3d-discovery455/final-review.json').read_text())['scoped_inventory_passed']
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc');assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
space=require_space(P,20+8/1024);P.mkdir();shutil.copyfile(K/'runner.c',P/'runner.c')
cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',str(P/'headers.d'),'-o',str(P/'run456.exe'),str(P/'runner.c'),'-lkernel32','-luser32','-ladvapi32']
r=dict(command=cmd,space=space,compiler_sha256=sha(cc),source_sha256=sha(P/'runner.c'),host_execution=False,rows=[])
with (P/'build.log').open('xb') as f:r['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
r['log_sha256']=sha(P/'build.log')
if r['exit_code']==0:
 deps=(P/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split();r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/'runner.c'}
 for p in [P/'run456.exe',Path('/home/paul/xbox-windows-native/d3d-discovery455-runner-build001/d3d.exe')]:r['rows'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n');assert r['exit_code']==0
assert r['rows'][1]['sha256']=='577bd78e1aae562eef1c7bc8c5d500f604e0d340fca50ea553504608dafdb143'
print('Physical controller compiled; same qualified lifecycle sample.')
