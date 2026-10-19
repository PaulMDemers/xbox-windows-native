"""Fresh sample and bounded runner builds; no executable is run on this host."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/scene-cost550-runner-build001')
sdk=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=sdk/'i386/bin/i686-w64-mingw32-gcc'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
assert json.loads((K/'host-tests002.json').read_text())['passed']
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(P,20+16/1024);P.mkdir()
scene=Path('/home/paul/xbox-windows-native/d3d-window547-runner-build001/d3d.exe')
assert sha(scene)=='4073e0a0f5a62a483d11a12b573ffbf7bbb1f2a914a835e7a25364cbdf49d436'
shutil.copyfile(scene,P/'scene.exe')
copied=P/'scenebench.c';shutil.copyfile(W/'src/samples/graphics-ladder/scenebench.c',copied)
shutil.copyfile(K/'runner.c',P/'runner.c');rows=[]
for stem,exe,receipt,libs in [('scenebench','bench.exe','sample-build001.json',['kernel32','user32','gdi32']),('runner','run550.exe','build001.json',['kernel32','user32','advapi32'])]:
 out=K/receipt;assert not out.exists()
 cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-MD','-MF',str(P/(stem+'.d')),'-o',str(P/exe),str(P/(stem+'.c'))]+['-l'+lib for lib in libs]
 r=dict(command=cmd,compiler=str(cc),compiler_sha256=sha(cc),source_sha256=sha(P/(stem+'.c')),host_execution=False,space=space)
 with (P/(stem+'.log')).open('xb') as f:r['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
 r['log_sha256']=sha(P/(stem+'.log'))
 if not r['exit_code']:
  deps=(P/(stem+'.d')).read_text().replace('\\\n','').split(': ',1)[1].split()
  r['headers']={n:sha(Path(n)) for n in sorted(set(deps)) if Path(n)!=P/(stem+'.c')}
  r.update(executable_sha256=sha(P/exe),executable_bytes=(P/exe).stat().st_size)
  rows.append(dict(path=str(P/exe),sha256=sha(P/exe),bytes=(P/exe).stat().st_size))
  if stem=='runner':r['rows']=list(reversed(rows))+[dict(path=str(P/'scene.exe'),sha256=sha(P/'scene.exe'),bytes=(P/'scene.exe').stat().st_size)]
 out.write_text(json.dumps(r,indent=2)+'\n');assert not r['exit_code'],(P/(stem+'.log')).read_text()
print('D3D presentation sample and private runner compiled.')
