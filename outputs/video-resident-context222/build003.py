"""Build/test the exact resident CPU ownership prefix; no guest or GPU launch."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'tools'));from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/build003';dest=k/'build003.json';assert not out.exists() and not dest.exists()
space=require_space(out);out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gcc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
lib=Path('/home/paul/xbox-windows-native/build/fatx-dump-map-001/build-fatx/ntoskrnl/CMakeFiles/libntoskrnl.dir/libntoskrnl.a')
assert sha(gcc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
assert sha(lib)=='7ddceef5d09b6d754f7003d92df45890dfbf56f2230361c0546b8f162812e940'
hal=k.parent/'video-staging-probe213/artifacts/build003/inputs/hal/halx86/CMakeFiles/libhal.dir/libhal.a'
assert sha(hal)=='aae2bf7d86d733ec9f6fc3983624a90badf73f629f13e17e6feb1fcf1bc191d8'
r=dict(status='started',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,
       source_pins={p.name:sha(p) for p in k.iterdir() if p.suffix in ['.c','.h','.py','.ps1']},
       compiler_sha256=sha(gcc),import_archive_sha256=sha(lib),hal_archive_sha256=sha(hal),commands=[],host_runs=[],native={},
       physical_access=False,guest_launch=False,gpu_access=False)
def command(argv,label):
    r['commands'].append(argv)
    with (out/(label+'.txt')).open('x') as f:subprocess.run(argv,check=True,stdout=f,stderr=subprocess.STDOUT)
try:
    host=Path('/usr/bin/gcc');r['host_compiler_sha256']=sha(host.resolve())
    r['host_compiler_version']=subprocess.check_output([str(host),'--version'],text=True).splitlines()[0]
    for level in ['0','2']:
        exe=out/('host-O'+level)
        command([str(host),'-std=c11','-O'+level,'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',str(k/'context.c'),str(k/'test.c'),'-o',str(exe)],'host-build-O'+level)
        command([str(exe)],'host-run-O'+level)
        text=(out/('host-run-O'+level+'.txt')).read_text();assert 'PASS concurrent_leases=512' in text
        r['host_runs'].append(dict(optimization=level,passed=True,log_sha256=sha(out/('host-run-O'+level+'.txt'))))
    common=[str(gcc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin']
    command(common+['-I/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/ddk','-D_WIN32_WINNT=0x0500','-DNTDDI_VERSION=0x05000000','-shared','-Wl,--entry,_DriverEntry@8','-Wl,--subsystem,native:5.0','-Wl,--image-base,0x10000','-Wl,--file-alignment,512','-Wl,--section-alignment,4096','-o',str(out/'resident.sys'),str(k/'context.c'),str(k/'driver.c'),str(lib),str(hal)],'native-driver')
    command(common+['-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-ladvapi32','-luser32'],'native-probe')
    for name in ['resident.sys','probe.exe']:r['native'][name]=dict(sha256=sha(out/name),bytes=(out/name).stat().st_size)
    r['status']='compiled_host_tests_passed'
except Exception as exc:r.update(status='preserved_failure',error=repr(exc));raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
