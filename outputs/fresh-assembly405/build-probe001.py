import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/probe001')
assert not P.exists() and os.environ.get('XWN_BUILD_LEASE')=='held';P.mkdir()
cc=Path('/home/paul/xbox-windows-native/release-readiness403-bootstrap001/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(cc)=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
cmd=[str(cc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',str(P/'probe.exe'),str(K/'probe001.c'),'-lkernel32','-luser32','-ladvapi32','-lgdi32','-lwinmm']
with (P/'build.log').open('xb') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
r=dict(command=cmd,exit_code=p.returncode,source_sha256=sha(K/'probe001.c'),compiler_sha256=sha(cc))
if not p.returncode:r['artifact']=dict(path=str(P/'probe.exe'),sha256=sha(P/'probe.exe'))
(K/'probe-build001.json').write_text(json.dumps(r,indent=2)+'\n');assert p.returncode==0
print('Fresh witness compiled',r['artifact']['sha256'])
