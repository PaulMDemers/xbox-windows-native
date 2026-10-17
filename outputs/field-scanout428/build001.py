"""Pinned no-CRT NT5 user-mode probe; no SDK or driver changes."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('/mnt/e/xwn428/build001')
sys.path.insert(0,str(W/'tools'));from build_space import require_space
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists() and not (K/'build001.json').exists()
space=require_space(P,20+8/1024)
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
P.mkdir(parents=True)
for n in ['probe.c','pattern.h']:(P/n).write_bytes((K/n).read_bytes())
cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-Wl,-Map,'+str(P/'probe.map'),'-o',str(P/'probe.exe'),str(P/'probe.c'),'-lkernel32','-luser32','-lgdi32']
r=dict(space=space,compiler_sha256=sha(cc),inputs={n:sha(P/n) for n in ['probe.c','pattern.h']},command=cmd)
with (P/'compile.log').open('xb') as f:r['exit_code']=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=90).returncode
r['log_sha256']=sha(P/'compile.log');r['compiled']=r['exit_code']==0
if r['compiled']:r.update(binary_sha256=sha(P/'probe.exe'),binary_bytes=(P/'probe.exe').stat().st_size)
(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
assert r['compiled'],(P/'compile.log').read_text()
print('428 probe compiled with no warnings')
