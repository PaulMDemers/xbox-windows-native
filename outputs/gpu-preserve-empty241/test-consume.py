"""Actual compiled241 consume/wait functions, real QEMU atomics, bounded adapters."""
import json,hashlib,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'consume-test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored'] and b['changed_sources']==['hw/xbox/nv2a/pfifo.c']
src=k/'artifacts/build001/source';out=k/'artifacts/consume-test001';out.mkdir(exist_ok=False);pins=read(k/'candidate001-source-pins.json')
for n in ['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h']:
 p=src/n;assert sha(p)==pins[n];q=out/('qemu/'+p.name if n.startswith('include/') else p.name);q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
p=src/'hw/xbox/nv2a/pfifo.c';assert sha(p)==pins['hw/xbox/nv2a/pfifo.c'];s=p.read_text(encoding='utf-8')
(out/'budget-actual.inc').write_text(s[s.index('typedef struct PFIFOConsume232'):s.index('static void pfifo_run_pusher')],encoding='utf-8')
(out/'wait-actual.inc').write_text(s[s.index('static unsigned pfifo_wait232'):s.index('static bool pfifo_budget232')],encoding='utf-8')
(out/'consume-actual.inc').write_text(s[s.index('void nv2a_preserve232_consume'):s.index('void *pfifo_thread')],encoding='utf-8')
(out/'test-consume.c').write_bytes((k/'test-consume.c').read_bytes())
r=dict(passed=False,compiled_pfifo_sha256=sha(p),actual_helpers={p.name:sha(p) for p in out.glob('*actual.inc')},runs=[],scope='Actual compiled consume/wait functions and real QEMU atomics under clock/FIFO/pusher adapters; not GL behavior, scheduling or ownership',physical_access=False,guest_launch=False)
try:
 for level in ['0','2']:
  exe=out/('consume-O'+level);cmd=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(out),str(out/'test-consume.c'),'-o',str(exe)]
  build=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert build.returncode==0,build.stderr
  result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120)
  r['runs'].append(dict(command=cmd,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,executable_sha256=sha(exe)));assert result.returncode==0 and not result.stderr
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('241 actual compiled consume O0/O2 ASan/UBSan PASS')
