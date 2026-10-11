"""Once-only actual bridge tuple-check code under ASan/UBSan, no renderer."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'callback-review001.json';assert not dest.exists()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/callback001';out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 inputs={n:sha(k/n) for n in ['callback-check.h','callback-check.c','test-callback-check.c','test-callbacks.py']},
 guest_launch=False,gl_executed=False,physical_access=False)
try:
 r['build_command']=['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'callback-check.c'),str(k/'test-callback-check.c'),'-o',str(out/'test')]
 with (out/'build.log').open('xb') as log:subprocess.run(r['build_command'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
 with (out/'run.log').open('xb') as log:subprocess.run([str(out/'test')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
 r['output']=(out/'run.log').read_text();assert 'PASS' in r['output']
 r.update(passed=True,run_log_sha256=sha(out/'run.log'),binary_sha256=sha(out/'test'))
except BaseException as e:r['error']=repr(e);raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print(r['output'])
