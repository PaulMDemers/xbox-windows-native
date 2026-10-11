"""Test actual compiled worker helper with explicit lock/GL/time adapters."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'worker-test001.json';assert not dest.exists()
out=k/'artifacts/worker-test001';out.mkdir(exist_ok=False);src=k/'artifacts/build004/source';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=(k/'worker.c').read_text();assert h in (src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
(out/'worker-actual.inc').write_text(h);(out/'test.c').write_bytes((k/'test-worker.c').read_bytes())
for name in ['atomic.h','compiler.h','queue.h']:
 p=out/'qemu'/name;p.parent.mkdir(exist_ok=True);p.write_bytes((src/'include/qemu'/name).read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),helper_sha256=sha(k/'worker.c'),renderer_sha256=sha(src/'hw/xbox/nv2a/pgraph/gl/renderer.c'),runs=[],scope='Actual compiled helper/primary atomics; adapters are not runtime GL evidence',physical_access=False)
try:
 for level in ['0','2']:
  exe=out/('test-O'+level);argv=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-isystem',str(out),str(out/'test.c'),'-o',str(exe)]
  b=subprocess.run(argv,capture_output=True,text=True,timeout=120);assert b.returncode==0,b.stderr
  x=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);r['runs'].append(dict(command=argv,exit_code=x.returncode,stdout=x.stdout,stderr=x.stderr,executable_sha256=sha(exe)))
  assert x.returncode==0 and not x.stderr
 r['passed']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('247 actual worker helper O0/O2 ASan/UBSan PASS')
