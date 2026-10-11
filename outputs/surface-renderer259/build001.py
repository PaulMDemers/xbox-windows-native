"""Build the new259 renderer-mode probe only; never modify258 or launch a guest."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'tools'));from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=k/'artifacts/build001';dest=k/'build001.json';assert not out.exists() and not dest.exists()
space=require_space(out);out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gcc=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc')
assert sha(gcc)=='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
old=k.parent/'surface-pattern258';b=json.loads((old/'build002.json').read_text())
assert sha(old/'arena.h')==b['input_pins']['arena.h']
assert sha(old/'artifacts/build002/pattern.sys')=='eba5d954d9075700a1a94b8196377626862bf74767b0bfbfe5c104d528a457a1'
inputs=['probe.c','expected.h','emit-expected.c','build001.py']
r=dict(passed=False,physical_access=False,guest_launch=False,gl_executed=False,
 started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,
 input_pins={n:sha(k/n) for n in inputs},driver_sha256=sha(old/'artifacts/build002/pattern.sys'),
 inherited_arena_header_sha256=sha(old/'arena.h'),compiler_sha256=sha(gcc),commands=[])
def cmd(args,label,output=None):
    r['commands'].append(args)
    with (out/(label+'.txt')).open('xb') as log:
        if output:
            with (out/output).open('xb') as target:subprocess.run(args,stdout=target,stderr=log,check=True,timeout=60)
        else:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
try:
    cmd(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(k/'emit-expected.c'),'-o',str(out/'emit')],'host-build')
    cmd([str(out/'emit')],'host-run','expected.bin')
    cmd([str(gcc),'-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin',
         '-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-Wl,--image-base,0x16000000',
         '-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-ladvapi32','-luser32'],'native-build')
    r.update(passed=True,native_sha256=sha(out/'probe.exe'),native_bytes=(out/'probe.exe').stat().st_size,expected_sha256=sha(out/'expected.bin'))
except BaseException as exc:r['error']=repr(exc);raise
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print('259 native probe compiled; no guest launch')
