"""Compile and execute actual C wait policy with controlled observations."""
import hashlib,json,pathlib,shutil,subprocess
K=pathlib.Path(__file__).resolve().parent;out=K/'host-tests001.json'
P=pathlib.Path('/mnt/c/xwn593/host001');assert not out.exists() and not P.exists()
assert shutil.disk_usage('/mnt/c').free-16*1024**2>=20*1024**3
P.mkdir(parents=True);r=dict(passed=False,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [K/'test_wait.c',K/'save_wait_policy.h']},scope='Actual wait-policy C execution with fake clock/probe; not Windows I/O or game proof')
try:
 cmd=['gcc','-std=c99','-Wall','-Wextra','-Werror','-O2','-o',str(P/'test_wait'),str(K/'test_wait.c')]
 a=subprocess.run(cmd,capture_output=True,text=True,timeout=60);r.update(compile_code=a.returncode,compile_stdout=a.stdout,compile_stderr=a.stderr);assert a.returncode==0
 b=subprocess.run([str(P/'test_wait')],capture_output=True,text=True,timeout=30);r.update(run_code=b.returncode,stdout=b.stdout,stderr=b.stderr);assert b.returncode==0 and b.stdout.count('passed')==11
 r['passed']=True
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(r['stdout'])
