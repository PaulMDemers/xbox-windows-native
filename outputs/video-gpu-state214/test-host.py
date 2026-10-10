"""Bounded exact-helper fault/read/once coverage with sanitizers; no MMIO authority."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;assert sys.platform=='linux';dest=k/'host-tests001.json';art=k/'artifacts/host001'
assert not dest.exists() and not art.exists();art.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,source_pins={n:sha(k/n) for n in ['test-host.py','host-test.c','host-shim/ntddk.h','gpu_snapshot.c','registers.h']},runs=[],physical_access=False,guest_launch=False)
try:
 for mode in [0,1]:
  exe=art/('test%d'%mode);cmd=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DXWN_GPU_SNAPSHOT='+str(mode),'-I'+str(k/'host-shim'),str(k/'host-test.c'),'-o',str(exe)]
  subprocess.run(cmd,check=True);p=subprocess.run([str(exe)],capture_output=True,text=True)
  (art/('mode%d.txt'%mode)).write_text(p.stdout+p.stderr)
  r['runs'].append(dict(mode=mode,command=cmd,binary_sha256=sha(exe),stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode));assert p.returncode==0
 r['passed']=True
finally:
 r['limits']='Mock reads/IRQL and CPU atomic once gate. Exact approved addresses, values/order, five faults,32 same-phase callers,unchanged source words. No hardware read semantics,ownership,atomic GPU state or runtime proof.'
 dest.write_text(json.dumps(r,indent=2)+'\n')
print('Exact host snapshot coverage PASS')
