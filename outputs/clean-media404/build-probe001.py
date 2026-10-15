import hashlib,json,subprocess,shlex,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=Path('/home/paul/xbox-windows-native/clean-media404-build001');out.mkdir(exist_ok=False)
r=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1')
sys.path.insert(0,str(W/'tools'));from toolchain_receipt import verify
verify(r,r.parent/'toolchain.json',json.loads((W/'upstream/dependencies.json').read_text()))
cmd=[str(r/'i386/bin/i686-w64-mingw32-gcc'),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',str(out/'PROBE.EXE'),str(K/'probe.c'),'-lkernel32','-luser32','-ladvapi32']
with (out/'build.log').open('x') as log:p=subprocess.run([str(r/'RosBE.sh'),str(out),'0','i386'],input='set -e\n'+shlex.join(cmd)+'\n',text=True,stdout=log,stderr=subprocess.STDOUT,timeout=120)
record={'command':cmd,'exit_code':p.returncode,'source_sha256':hashlib.sha256((K/'probe.c').read_bytes()).hexdigest()}
if p.returncode==0:record['binary_sha256']=hashlib.sha256((out/'PROBE.EXE').read_bytes()).hexdigest()
(K/'probe-build001.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(p.returncode)
