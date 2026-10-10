"""Compile/test matched224 read OFF/ON variants; never launch a guest here."""
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
       compiler_sha256=sha(gcc),kernel_archive_sha256=sha(lib),hal_archive_sha256=sha(hal),commands=[],host_runs=[],native={},
       physical_access=False,guest_launch=False,gpu_writes=False,passed=False)
def cmd(argv,label):
    r['commands'].append(argv)
    with (out/(label+'.txt')).open('x') as log:subprocess.run(argv,check=True,stdout=log,stderr=subprocess.STDOUT)
try:
    for mode in [0,1]:
        exe=out/('bridge-'+str(mode))
        cmd(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-DX224_READS='+str(mode),'-I'+str(k/'host-include'),str(k/'test-bridge.c'),str(k/'context.c'),str(k/'retirement.c'),'-o',str(exe)],'bridge-build-'+str(mode))
        cmd([str(exe)],'bridge-run-'+str(mode));assert (out/('bridge-run-'+str(mode)+'.txt')).read_text().startswith('PASS actual_driver_bridge')
        r['host_runs'].append(dict(kind='actual_bridge',reads=mode,log_sha256=sha(out/('bridge-run-'+str(mode)+'.txt'))))
    exe=out/'sampler'
    cmd(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(k/'retirement.c'),str(k/'test-retirement.c'),'-o',str(exe)],'sampler-build')
    cmd([str(exe)],'sampler-run');assert 'PASS DMA_state_cases=65536' in (out/'sampler-run.txt').read_text()
    r['host_runs'].append(dict(kind='sampler',log_sha256=sha(out/'sampler-run.txt')))
    common=[str(gcc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin']
    for name in ['context','retirement']:
        cmd(common+['-c',str(k/(name+'.c')),'-o',str(out/(name+'.o'))],'shared-'+name)
    for case,mode in [('control001',0),('candidate001',1)]:
        p=out/case;p.mkdir()
        cmd(common+['-I/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/ddk','-D_WIN32_WINNT=0x0500','-DNTDDI_VERSION=0x05000000','-DX224_READS='+str(mode),'-shared','-Wl,--entry,_DriverEntry@8','-Wl,--subsystem,native:5.0','-Wl,--image-base,0x10000','-Wl,--file-alignment,512','-Wl,--section-alignment,4096','-o',str(p/'resident.sys'),str(out/'context.o'),str(out/'retirement.o'),str(k/'driver.c'),str(lib),str(hal)],case+'-native')
        r['native'][case]=dict(sha256=sha(p/'resident.sys'),bytes=(p/'resident.sys').stat().st_size)
    cmd(common+['-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-ladvapi32','-luser32'],'native-probe')
    r['native']['probe.exe']=dict(sha256=sha(out/'probe.exe'),bytes=(out/'probe.exe').stat().st_size)
    r['shared_objects']={n:sha(out/n) for n in ['context.o','retirement.o']};r['passed']=True
except Exception as e:r['error']=repr(e);raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n');print('224 build',r['passed'])
