"""Fresh compile from exact 313 source/tool pins; no guest launch."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
W=K.parents[1]
OLD=W/'outputs/hd-ui313'
OUT=Path('/mnt/e/xwn329/helper001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not OUT.exists() and not (K/'helper001.json').exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>20*1024**3
cc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((OLD/'build001.json').read_text())
review=json.loads((OLD/'build-review001.json').read_text())
assert sha(cc)==review['compiler_sha256']
OUT.mkdir(parents=True)
for name in ['wizard313.c','activation.inc','activation.h','policy.h']:
    assert sha(OLD/name)==prior['files'][name]
    shutil.copyfile(OLD/name,OUT/name)
args=[str(cc),'-DXWN_EMULATOR_ACTIVATION313=1','-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o','wizard.exe','wizard313.c','-lkernel32','-luser32']
with (OUT/'compiler.log').open('wb') as log:
    run=subprocess.run(args,cwd=OUT,stdout=log,stderr=subprocess.STDOUT,timeout=120)
r=dict(compiler_sha256=sha(cc),command=args,exit_code=run.returncode,original_binary_sha256=review['binary_sha256'],physical_access=False,guest_launch=False)
if run.returncode==0:
    r.update(sha256=sha(OUT/'wizard.exe'),bytes=(OUT/'wizard.exe').stat().st_size,original_binary_match=sha(OUT/'wizard.exe')==review['binary_sha256'])
r['files']={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}
(K/'helper001.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
assert run.returncode==0
