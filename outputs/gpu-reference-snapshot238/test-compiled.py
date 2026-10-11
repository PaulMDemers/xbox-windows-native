"""Exact compiled234 helpers/233 fill; explicit adapters, real QEMU atomics."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
b=read(k/'build001.json');assert b['passed'] and b['borrowed_sources_restored']
src=k/'artifacts/build001/source';out=k/'artifacts/test001';out.mkdir(exist_ok=False)
pins=read(k/'candidate001-source-pins.json')
for n in ['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h']:
 p=src/n;assert sha(p)==pins[n];q=out/('qemu/'+p.name if n.startswith('include/') else p.name);q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
head=(src/'hw/xbox/nv2a/nv2a_int.h').read_text();pg=(src/'hw/xbox/nv2a/pgraph/pgraph.c').read_text();nv=(src/'hw/xbox/nv2a/nv2a.c').read_text()
(out/'row-actual.inc').write_text(head[head.index('#define NV2A_WAIT233_CAPACITY'):head.index('typedef struct NV2AState')])
(out/'wait-actual.inc').write_text(pg[pg.index('void nv2a_wait233_fill'):pg.index('uint64_t pgraph_read')])
(out/'snapshot-actual.inc').write_text(nv[nv.index('/*238 ONE request'):nv.index('static void nv2a_realize')])
renderer=(src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
a=renderer.index('    /*238 FIFO-owned');b=renderer.index('    /* Request is one-shot',a)
(out/'worker-actual.inc').write_text('static void actual_worker(NV2AState *d) { PGRAPHState *pg=&d->pgraph; PGRAPHGLState *r=pg->gl_renderer_state;\n'+renderer[a:b]+'}\n')
(out/'test-snapshot.c').write_bytes((k/'test-compiled.c').read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),test_sha256=sha(k/'test-compiled.c'),actual_helpers={p.name:sha(p) for p in out.glob('*actual.inc')},runs=[],physical_access=False,guest_launch=False,scope='Compiled copy/request/report/publication and ring with real QEMU atomics; explicit host clock/register/FIFO/mutex/object/string adapters, not QEMU scheduling or GPU ownership.')
try:
 for level in ['0','2']:
  exe=out/('snapshot-O'+level);cmd=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-I'+str(out),str(out/'test-snapshot.c'),'-o',str(exe)]
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert c.returncode==0,c.stderr
  run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=180)
  r['runs'].append(dict(command=cmd,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,executable_sha256=sha(exe)))
  assert run.returncode==0 and not run.stderr,run.stderr
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('234 compiled snapshot race/boundary checks PASS')
