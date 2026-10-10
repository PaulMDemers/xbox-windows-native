"""Exercise byte-pinned actual ring/fill, with explicit clock/PG/FIFO adapters."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;build=sys.argv[1];case=sys.argv[2]
assert build in ['build001','build002'] and case in ['test001','test002']
dest=k/(case+'.json');assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
b=read(k/(build+'.json'));assert b['passed'] and b['borrowed_sources_restored']
source=k/'artifacts'/build/'source';out=k/'artifacts'/case;out.mkdir(exist_ok=False)
pins=read(k/('candidate001-source-pins.json' if build=='build001' else 'candidate002-source-pins.json'))
for n in ['include/qemu/atomic.h','include/qemu/compiler.h','hw/xbox/nv2a/nv2a_regs.h']:
    p=source/n;assert sha(p)==pins[n];q=out/('qemu/'+p.name if n.startswith('include/') else p.name);q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
header=(source/'hw/xbox/nv2a/nv2a_int.h').read_text();pg=(source/'hw/xbox/nv2a/pgraph/pgraph.c').read_text()
row=header[header.index('#define NV2A_WAIT233_CAPACITY'):header.index('typedef struct NV2AState')]
helper=pg[pg.index('void nv2a_wait233_fill'):pg.index('uint64_t pgraph_read')]
(out/'row-actual.inc').write_text(row);(out/'wait-actual.inc').write_text(helper);(out/'test-wait.c').write_bytes((k/'test-wait.c').read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),test_sha256=sha(k/'test-wait.c'),build=build,actual_row_sha256=sha(out/'row-actual.inc'),actual_helper_sha256=sha(out/'wait-actual.inc'),runs=[],guest_launch=False,physical_access=False,
    scope='Actual ring/fill with host clock/register/FIFO adapters and caller pthread lock; not QEMU lock scheduling or GPU execution.')
try:
    for level in ['0','2']:
        exe=out/('wait-O'+level);cmd=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-I'+str(out),str(out/'test-wait.c'),'-o',str(exe)]
        c=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert c.returncode==0,c.stderr
        run=subprocess.run([str(exe)]+(['mask-only'] if case=='test001' else []),capture_output=True,text=True,timeout=120)
        r['runs'].append(dict(command=cmd,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,executable_sha256=sha(exe)))
        assert run.returncode==0 and not run.stderr,run.stderr
    r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('233 actual ring host checks PASS')
