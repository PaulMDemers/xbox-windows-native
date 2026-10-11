"""Once-only sanitizer build/test; no guest or renderer is invoked."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'admission-review002.json';assert not dest.exists()
assert sys.platform=='linux'
out=k/'artifacts/admission002';out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,guest_launch=False,gl_executed=False,physical_access=False,commands=[],
 inputs={n:sha(k/n) for n in ['admission.h','admission.c','test-admission.c','test-admission.py']})
try:
    build=['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'admission.c'),str(k/'test-admission.c'),'-o',str(out/'test')]
    r['commands'].append(build)
    with (out/'build.log').open('xb') as f:subprocess.run(build,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
    run=[str(out/'test')];r['commands'].append(run)
    with (out/'run.log').open('xb') as f:subprocess.run(run,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
    assert (out/'run.log').read_text().startswith('PASS admission_checks=')
    r.update(passed=True,result=(out/'run.log').read_text().strip(),log_sha256=sha(out/'run.log'),
       limits='Pure range/age refusal logic. Completeness bits and records need an actual reviewed runtime collector; not runtime ownership proof.')
except BaseException as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print(r['result'])
