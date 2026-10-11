"""Compile exact build005 callback and marker bodies with actual primary headers."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;src=k/'artifacts/build005/source';out=k/'artifacts/callback-test001';out.mkdir(exist_ok=False)
dest=k/'callback-test001.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
primary=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
pins=json.loads((k/'candidate005-source-pins.json').read_text())
p=primary/'include/hw/core/cpu.h';assert sha(p)==pins['include/hw/core/cpu.h'];t=p.read_text()
a=t.index('typedef struct MemAccessCallback {');z=t.index('} MemAccessCallback;',a)+len('} MemAccessCallback;')
(out/'callback-struct.inc').write_text(t[a:z]+'\n')
for name in ['atomic.h','compiler.h','queue.h']:
 p=out/'qemu'/name;p.parent.mkdir(exist_ok=True)
 origin=src/'include/qemu'/name
 if not origin.exists():origin=k.parent/'gpu-reference-pair242/artifacts/build005/source/include/qemu'/name
 assert sha(origin)==pins['include/qemu/'+name];p.write_bytes(origin.read_bytes())
p=src/'system/physmem.c';t=p.read_text();a=t.index('static void do_mem_access_callback_insert');z=t.index('void mem_check_access_callback_vaddr',a)
(out/'callback-actual.inc').write_text(t[a:z])
p=src/'hw/xbox/nv2a/nv2a.c';t=p.read_text();a=t.index('static void lifecycle244_mark_set');z=t.index('static void preserve227_set',a)
(out/'marker-actual.inc').write_text(t[a:z])
(out/'test-callback.c').write_bytes((k/'test-callback.c').read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),actual_inputs={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()},runs=[],physical_access=False,guest_launch=False,scope='Exact compiled callback/marker bodies with real QEMU queues/atomics and explicit work/clock/log adapters; not actual CPU thread or frontend runtime qualification')
try:
 for level in ['0','2']:
  exe=out/('callback-O'+level);argv=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-isystem',str(out),str(out/'test-callback.c'),'-o',str(exe)]
  build=subprocess.run(argv,capture_output=True,text=True,timeout=120);assert build.returncode==0,build.stderr
  result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);r['runs'].append(dict(command=argv,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,executable_sha256=sha(exe)))
  assert result.returncode==0 and not result.stderr
 r['passed']=True
except BaseException as exc:r['error']=repr(exc);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('244 actual callback/marker O0/O2 ASan/UBSan PASS')
