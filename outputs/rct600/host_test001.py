"""Compile and run exact portable pairing code independently of debugger transport."""
import hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'host-tests001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists()
exe=Path('/mnt/c/xwn600/host-calls001');assert not exe.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cmd=['/usr/bin/cc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(K/'host_calls.c'),'-o',str(exe)]
r=dict(passed=False,command=cmd,inputs={n:sha(K/n) for n in ['host_calls.c','calls.h']})
try:
 b=subprocess.run(cmd,capture_output=True,text=True,timeout=30);r['build']=dict(code=b.returncode,stdout=b.stdout,stderr=b.stderr);b.check_returncode()
 p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);r['run']=dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr);p.check_returncode()
 assert p.stdout=='CALLS600 PASS: thread sharing, recursion, stale sites, 9 rejection controls\n'
 r.update(passed=True,binary_sha256=sha(exe))
finally:out.write_text(json.dumps(r,indent=2)+'\n')
