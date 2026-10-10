"""Compile actual helper/report with byte-pinned QEMU atomic and compiler headers."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'publication-test001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((k/'build001.json').read_text());assert b['passed'] and b['borrowed_sources_restored']
pins=json.loads((k/'candidate001-source-pins.json').read_text())
source=k/'artifacts/build001/source'
out=k/'artifacts/publication-test001';out.mkdir(exist_ok=False)
for n in ['include/qemu/atomic.h','include/qemu/compiler.h']:
    p=source/n;assert sha(p)==pins[n];q=out/'qemu'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
p=source/'hw/xbox/nv2a/nv2a.c';assert sha(p)==pins['hw/xbox/nv2a/nv2a.c'];s=p.read_text()
a=s.index('static char *preserve227_report(');z=s.index('\n/*231 caller holds FIFO lock.',a)
c=s.index('void nv2a_preserve227_finish(');d=s.index('\nstatic void nv2a_realize(',c)
(out/'publication-actual.inc').write_text(s[a:z]+s[c:d])
(out/'test-publication.c').write_bytes((k/'test-publication.c').read_bytes())
flags=[]
results=[]
for level in ['0','2']:
    exe=out/('publication-O'+level)
    command=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-I'+str(out),str(out/'test-publication.c'),'-o',str(exe)]+flags
    compile=subprocess.run(command,capture_output=True,text=True,timeout=120);assert compile.returncode==0,compile.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=180);assert run.returncode==0 and not run.stderr,run.stderr
    assert 'concurrent_pairs=100000 publication_pairs=10000' in run.stdout,run.stdout
    results.append(dict(command=command,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,executable_sha256=sha(exe)))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),test_sha256=sha(k/'test-publication.c'),actual_helper_sha256=sha(out/'publication-actual.inc'),atomic_headers={n:pins[n] for n in ['include/qemu/atomic.h','include/qemu/compiler.h']},runs=results,scope='Actual helper/report and actual QEMU atomic macros. Host scheduling, object/clock/string-format adapters; no GPU, cross-architecture or guest qualification.'),indent=2)+'\n')
print('Actual QEMU atomic publication checks PASS')
