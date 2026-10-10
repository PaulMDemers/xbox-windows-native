"""Actual proposed staging planner: host pixel/extent tests, not GPU validation."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;assert sys.platform=='linux'
out=k/'artifacts/host001';dest=k/'host-tests001.json'
assert not out.exists() and not dest.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,guest_launch=False,physical_access=False,gpu_transfer_qualified=False,
 source_pins={p.name:sha(p) for p in [Path(__file__),k/'transfer_plan.h',k/'host-test.c']},runs=[])
try:
 for optimization in ['-O0','-O2']:
  exe=out/('planner'+optimization);cmd=['gcc','-std=c99',optimization,'-g','-Wall','-Wextra','-Werror',
   '-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'host-test.c'),'-o',str(exe)]
  subprocess.run(cmd,check=True);run=subprocess.run([str(exe)],check=True,text=True,capture_output=True)
  (out/(optimization+'.txt')).write_text(run.stdout+run.stderr)
  r['runs'].append(dict(command=cmd,binary_sha256=sha(exe),exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr))
 r['passed']=True
finally:
 r['limits']='Host-only independent bitmap/guard/extent oracle for the actual planner. No allocation, ABI invocation, cache visibility, DMA submission, completion or timing evidence.'
 dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
