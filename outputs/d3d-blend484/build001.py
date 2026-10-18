"""Build PC-only two-case controller and pin alpha sample build001."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/home/paul/xbox-windows-native/d3d-blend484-runner-build001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not (K/'build001.json').exists()
sample=Path('/home/paul/xbox-windows-native/blend484-build001');b=json.loads((sample/'build.json').read_text())
assert b['exit_code']==0 and sha(W/'src/samples/graphics-ladder/blend.c')==b['source_sha256'] and sha(sample/'blend.exe')==b['executable_sha256']
assert not (K/'sample-build001.json').exists();shutil.copyfile(sample/'build.json',K/'sample-build001.json')
cc=Path(b['compiler']);assert sha(cc)==b['compiler_sha256']=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
space=require_space(P,20+8/1024);P.mkdir();shutil.copyfile(K/'runner.c',P/'runner.c');shutil.copyfile(sample/'blend.exe',P/'d3d.exe')
cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',str(P/'headers.d'),'-o',str(P/'run484.exe'),str(P/'runner.c'),'-lkernel32','-luser32','-ladvapi32']
r=dict(command=cmd,space=space,compiler_sha256=sha(cc),source_sha256=sha(P/'runner.c'),host_execution=False,rows=[])
with (P/'build.log').open('xb') as f:r['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
r['log_sha256']=sha(P/'build.log')
if r['exit_code']==0:
 deps=(P/'headers.d').read_text().replace('\\\n','').split(': ',1)[1].split();r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/'runner.c'}
 for p in [P/'run484.exe',P/'d3d.exe']:r['rows'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n');assert r['exit_code']==0
print('Controller compiled; alpha sample copied byte-exact, no execution.')
