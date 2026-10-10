"""Actual native probe with injected allocation/physical/copy/IRQL failures."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;assert sys.platform=='linux'
out=k/'artifacts/host002';dest=k/'host-tests002.json';assert not out.exists() and not dest.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,guest_launch=False,gpu_transfer_qualified=False,runs=[],
 source_pins={str(p.relative_to(k)):sha(p) for p in [Path(__file__),k/'host-test.c',k/'host-shim/ntddk.h',k/'staging_probe.c']},
 planner_sha256=sha(k.parent/'video-gpu-transfer-contract212/transfer_plan.h'))
try:
 for mode in [0,1]:
  exe=out/('test%d'%mode);cmd=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-DXWN_STAGING_PROBE='+str(mode),'-I'+str(k/'host-shim'),
    '-I'+str(k.parent/'video-gpu-transfer-contract212'),str(k/'host-test.c'),'-o',str(exe)]
  subprocess.run(cmd,check=True);p=subprocess.run([str(exe)],text=True,capture_output=True)
  (out/('mode%d.txt'%mode)).write_text(p.stdout+p.stderr)
  r['runs'].append(dict(mode=mode,command=cmd,binary_sha256=sha(exe),stdout=p.stdout,stderr=p.stderr,exit_code=p.returncode))
  assert p.returncode==0
 r['passed']=True
finally:
 r['limits']='Host fault-injection coverage of the exact helper. Providers are mocks: no proof of NT5 allocation, ABI, physical contiguity, cache, DMA or crash behavior.'
 dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
