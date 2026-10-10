"""Actual unchanged driver bridge, host callbacks only; new unique output guard."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'artifacts/bridge001';dest=k/'bridge001.json'
assert not out.exists() and not dest.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(physical_access=False,guest_launch=False,native_runtime_qualified=False,passed=False,
       inputs={str(p.relative_to(k)):sha(p) for p in [k/'driver.c',k/'context.c',k/'context.h',k/'test-bridge.c',k/'host-include/ddk/ntddk.h',Path(__file__)]},runs=[])
try:
    for level in ['0','2']:
        exe=out/('host-O'+level)
        command=['gcc','-std=c11','-O'+level,'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(k/'host-include'),str(k/'test-bridge.c'),str(k/'context.c'),'-o',str(exe)]
        with (out/('compile-O'+level+'.txt')).open('x') as log:subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
        with (out/('run-O'+level+'.txt')).open('x') as log:subprocess.run([str(exe)],check=True,stdout=log,stderr=subprocess.STDOUT)
        assert (out/('run-O'+level+'.txt')).read_text().startswith('PASS actual_driver_bridge')
        r['runs'].append(dict(optimization=level,command=command,log_sha256=sha(out/('run-O'+level+'.txt'))))
    r['passed']=True
except Exception as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n');print('Bridge host tests',r['passed'])
