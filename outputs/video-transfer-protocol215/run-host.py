"""Unique host-only exact-source ASan/UBSan attempts; no native or guest launch."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];assert attempt in ['host001','host002','host003']
dest=k/(attempt+'.json');assert not dest.exists();art=k/'artifacts'/attempt;art.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=dict(passed=False,host_only=True,guest_launch=False,physical_access=False,source_sha256=sha(Path(__file__)),source_pins={},runs=[])
assert shutil.disk_usage('/mnt/c').free>=20*1024**3
for n in ['protocol.h','protocol.c','model-values.h','test.c']:
 q=art/n;q.write_bytes((k/n).read_bytes());r['source_pins'][n]=sha(q)
compiler=Path(shutil.which('gcc')).resolve();r['compiler_path']=str(compiler);r['compiler_sha256']=sha(compiler)
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:abort_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
try:
 for optimize in ['-O0','-O2']:
  output=art/('test'+optimize[-1]);cmd=[str(compiler),'-std=c11',optimize,'-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(art/'protocol.c'),str(art/'test.c'),'-o',str(output)]
  build=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
  row=dict(command=cmd,compile_exit=build.returncode,compile_stdout=build.stdout,compile_stderr=build.stderr);r['runs'].append(row)
  assert build.returncode==0
  row['binary_sha256']=sha(output)
  trial=subprocess.run([str(output)],env=env,capture_output=True,text=True,timeout=60)
  row.update(exit_code=trial.returncode,stdout=trial.stdout,stderr=trial.stderr)
  assert trial.returncode==0 and not trial.stderr and 'pixel_cases=1024 descriptor_cases=100000' in trial.stdout
 r['passed']=True
except Exception as exc:r['error']=repr(exc);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
