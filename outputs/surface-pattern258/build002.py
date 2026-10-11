"""Compile/test dedicated258 reboot-held arena; never launch a guest here."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'tools'));from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/build002';dest=k/'build002.json';assert not out.exists() and not dest.exists()
space=require_space(out);out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gcc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
lib=Path('/home/paul/xbox-windows-native/build/fatx-dump-map-001/build-fatx/ntoskrnl/CMakeFiles/libntoskrnl.dir/libntoskrnl.a')
hal=k.parent/'video-staging-probe213/artifacts/build003/inputs/hal/halx86/CMakeFiles/libhal.dir/libhal.a'
assert sha(gcc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
assert sha(lib)=='7ddceef5d09b6d754f7003d92df45890dfbf56f2230361c0546b8f162812e940'
assert sha(hal)=='aae2bf7d86d733ec9f6fc3983624a90badf73f629f13e17e6feb1fcf1bc191d8'
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,
       input_pins={str(p.relative_to(k)):sha(p) for p in k.rglob('*') if p.is_file() and 'artifacts' not in p.parts},
       host_header_sha256=sha(k.parent/'video-fifo-retirement224/host-include/ddk/ntddk.h'),
       compiler_sha256=sha(gcc),kernel_archive_sha256=sha(lib),hal_archive_sha256=sha(hal),commands=[],host_runs=[],native={},
       physical_access=False,guest_launch=False,gpu_writes=False,passed=False)
def cmd(argv,label):
    r['commands'].append(argv)
    with (out/(label+'.txt')).open('x') as log:subprocess.run(argv,check=True,stdout=log,stderr=subprocess.STDOUT)
try:
    for name,files,flags in [
        ('core',['arena.c','test-arena.c'],['-pthread']),
        ('bridge',['arena.c','test-bridge.c'],['-I'+str(k.parent/'video-fifo-retirement224/host-include')])]:
        exe=out/name
        cmd(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer']+flags+[str(k/f) for f in files]+['-o',str(exe)],name+'-build')
        cmd([str(exe)],name+'-run');assert (out/(name+'-run.txt')).read_text().startswith('PASS actual_')
        r['host_runs'].append(dict(kind=name,log_sha256=sha(out/(name+'-run.txt'))))
    common=[str(gcc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin']
    cmd(common+['-c',str(k/'arena.c'),'-o',str(out/'arena.o')],'arena-object')
    cmd(common+['-I/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/ddk','-D_WIN32_WINNT=0x0500','-DNTDDI_VERSION=0x05000000','-shared','-Wl,--entry,_DriverEntry@8','-Wl,--subsystem,native:5.0','-Wl,--image-base,0x10000','-Wl,--file-alignment,512','-Wl,--section-alignment,4096','-o',str(out/'pattern.sys'),str(out/'arena.o'),str(k/'driver.c'),str(lib),str(hal)],'native-driver')
    cmd(common+['-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-Wl,--image-base,0x15000000','-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-ladvapi32','-luser32'],'native-probe')
    for name in ['pattern.sys','probe.exe']:r['native'][name]=dict(sha256=sha(out/name),bytes=(out/name).stat().st_size)
    r['shared_objects']={'arena.o':sha(out/'arena.o')};r['passed']=True
except Exception as e:r['error']=repr(e);raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n');print('258 build',r['passed'])
