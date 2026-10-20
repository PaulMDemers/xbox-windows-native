"""Compile the exact shared phase decision and validate state transitions."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn605');out=K/'host-phase001.json'
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists()
space=require_space(O,20.02);O.mkdir(exist_ok=True);exe=O/'host-phase001';assert not exe.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,space=space,inputs={n:sha(K/n) for n in ['host_phase.c','phase.h']})
try:
 cmd=['/usr/bin/cc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(K/'host_phase.c'),'-o',str(exe)]
 b=subprocess.run(cmd,capture_output=True,text=True,timeout=30);r['build']=dict(command=cmd,code=b.returncode,stdout=b.stdout,stderr=b.stderr);b.check_returncode()
 p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);r['run']=dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr);p.check_returncode()
 assert p.stdout=='PHASE605 PASS: pending drain, one transition, 100 duplicate requests, 3 invalid states\n'
 r.update(passed=True,binary_sha256=sha(exe))
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('605 phase-state host controls passed')
