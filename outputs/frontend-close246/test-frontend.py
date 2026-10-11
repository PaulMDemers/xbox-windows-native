"""Actual compiled UI gate with explicit GL/renderer/BQL adapters and real atomics."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'frontend-test001.json';assert not dest.exists()
out=k/'artifacts/frontend-test001';out.mkdir(exist_ok=False);src=k/'artifacts/build001/source';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=(src/'ui/xemu.c').read_text();helper=(k/'frontend.c').read_text();assert helper in t
(out/'frontend-actual.inc').write_text(helper);(out/'test.c').write_bytes((k/'test-frontend.c').read_bytes())
for n in ['atomic.h','compiler.h']:
 p=out/'qemu'/n;p.parent.mkdir(exist_ok=True);p.write_bytes((src/'include/qemu'/n).read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),actual_frontend_sha256=sha(k/'frontend.c'),actual_ui_sha256=sha(src/'ui/xemu.c'),runs=[],physical_access=False,guest_launch=False,scope='Actual compiled helper/primary atomics with explicit GL/renderer/BQL/context adapters; not runtime GL completion evidence')
try:
 for level in ['0','2']:
  exe=out/('test-O'+level);argv=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-isystem',str(out),str(out/'test.c'),'-o',str(exe)]
  b=subprocess.run(argv,capture_output=True,text=True,timeout=120);assert b.returncode==0,b.stderr
  x=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);r['runs'].append(dict(command=argv,exit_code=x.returncode,stdout=x.stdout,stderr=x.stderr,executable_sha256=sha(exe)))
  assert x.returncode==0 and not x.stderr
 r['passed']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('246 actual gate O0/O2 ASan/UBSan,negative states and joined actor races PASS')
