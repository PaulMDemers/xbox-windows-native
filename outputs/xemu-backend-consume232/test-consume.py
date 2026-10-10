"""Extract actual compiled parser, budgets and masks; explicit PGRAPH/map adapters."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'consume-test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((k/'build001.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
pins=json.loads((k/'candidate001-source-pins.json').read_text());source=k/'artifacts/build001/source'
out=k/'artifacts/consume-test001';out.mkdir(exist_ok=False)
for n in ['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h']:
    p=source/n;assert sha(p)==pins[n];q=out/('qemu/'+p.name if n.startswith('include/') else p.name);q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
p=source/'hw/xbox/nv2a/pfifo.c';assert sha(p)==pins['hw/xbox/nv2a/pfifo.c'];s=p.read_text()
def section(a,z):
    start=s.index(a);return s[start:s.index(z,start)]
actual=section('typedef struct PFIFOConsume232','static uint32_t ramht_hash')
actual+=section('static bool can_fifo_access','/* If NV097_FLIP_STALL')
actual+=section('static bool pfifo_pusher_should_stall','void *pfifo_thread')
(out/'pusher-actual.inc').write_text(actual);(out/'test-consume.c').write_bytes((k/'test-consume.c').read_bytes())
results=[]
for level in ['0','2']:
    exe=out/('consume-O'+level);command=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(out),str(out/'test-consume.c'),'-o',str(exe)]
    compile=subprocess.run(command,capture_output=True,text=True,timeout=120);assert compile.returncode==0,compile.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);assert run.returncode==0 and not run.stderr,run.stderr
    assert 'packet_cases=10000' in run.stdout,run.stdout
    results.append(dict(command=command,stdout=run.stdout,stderr=run.stderr,exit_code=run.returncode,executable_sha256=sha(exe)))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),test_sha256=sha(k/'test-consume.c'),actual_parser_sha256=sha(out/'pusher-actual.inc'),compiled_pfifo_sha256=sha(p),runs=results,scope='Actual compiled DMA parser/masks/atomics and budget/wait wrapper; host-only PGRAPH, DMA-map and byte-load adapters. Does not qualify GPU execution or guest handoff.'),indent=2)+'\n')
print('Actual bounded pusher host checks PASS')
