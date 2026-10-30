"""Compile bounded LED transport/pulse tests; no console access."""
from pathlib import Path
import os,json,subprocess,hashlib
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn830/led-host001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
P.mkdir(parents=True);r={'passed':False,'physical_access':False}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc)
 r['sources']={str(p.relative_to(K)):sha(p) for p in [K/'led_host.c',K/'firmware/led830.c',K/'firmware/led830.h',K/'firmware/xcal_bus.h']}
 cmd=[str(cc),'-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined',str(K/'led_host.c'),str(K/'firmware/led830.c'),'-o',str(P/'test')]
 r['command']=cmd
 cp=subprocess.run(cmd,capture_output=True,timeout=30);(P/'build.log').write_bytes(cp.stdout+cp.stderr);assert cp.returncode==0,cp.stderr
 cp=subprocess.run([str(P/'test')],capture_output=True,timeout=30);(P/'run.log').write_bytes(cp.stdout+cp.stderr);assert cp.returncode==0,cp.stdout+cp.stderr
 r['result']=json.loads(cp.stdout);r['passed']=r['result']['passed']
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'led-host001.json').write_text(json.dumps(r,indent=2)+'\n')
print(r)
