"""Review exact compiled bounded reads/publication, existing gates and fresh ID."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in read(k/'emulator-frozen.json').items():assert sha(ws/path)==digest,path
build=read(k/'build004.json');assert build['passed'] and build['borrowed_sources_restored']
assert build['changed_sources']==['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c']
for name in ['inventory-test005','consume-test001','pair-test001','guard-test003','connection-test001','host-close-test001']:assert read(k/(name+'.json'))['passed'],name
assert read(k/'pair-test001.json')['actual_trace_source_sha256']==sha(k/'trace.py')
base=k.parent/'gpu-preserve-empty241/artifacts/build001/source';src=k/'artifacts/build004/source';nv=(src/'hw/xbox/nv2a/nv2a.c').read_text(encoding='utf-8');renderer=(src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text(encoding='utf-8')
for name in ['hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/pgraph.c']:assert sha(src/name)==sha(base/name)
before=(base/'hw/xbox/nv2a/nv2a.c').read_text(encoding='utf-8')
for start,end in [('static void preserve227_set','/*242 No monitor'),('void nv2a_preserve227_finish','/*238 ONE request')]:
 original_end='static char *preserve227_report' if end=='/*242 No monitor' else end
 assert nv[nv.index(start):nv.index(end)]==before[before.index(start):before.index(original_end)]
inventory=(k/'inventory.c').read_text(encoding='utf-8');assert inventory in renderer
assert all(word not in inventory for word in ['QTAILQ_REMOVE','glDelete','glGet','async_safe','qemu_thread_join','surface_download','qemu_event_wait'])
assert 'qemu_mutex_trylock(&r->shader_cache_lock)' in inventory and inventory.count('qemu_mutex_unlock(&r->shader_cache_lock)')==1
worker=renderer[renderer.index('    if (qatomic_load_acquire(&d->preserve227.state) == 1)'):renderer.index('    if (qatomic_read(&r->downloads_pending)')]
order=['inventory242_fifo(d, 0)','qemu_mutex_unlock(&d->pfifo.lock)','qemu_mutex_lock(&pg->lock)','inventory242_copy(d, 0)','pgraph_gl_preserve227(d)','inventory242_copy(d, 1)','qemu_mutex_unlock(&pg->lock)','qemu_mutex_lock(&d->pfifo.lock)','inventory242_fifo(d, 1)','nv2a_preserve227_finish(d, result)']
assert [worker.index(v) for v in order]==sorted(worker.index(v) for v in order)
report=nv[nv.index('static char *inventory242_report'):nv.index('static char *preserve227_report')]
assert 'qatomic_load_acquire(&d->preserve227.state)' in report and 'bool published = state == 3 || state == 4 || state == 6' in report and 'if (published)' in report
assert 'cpu_callbacks_observed=0 gl_bindings_observed=0 retired=0 native_grant=0' in report
trace=(k/'trace.py').read_text(encoding='utf-8');assert trace.count("qom-set '+path+' xwn-preserve227 true")==1 and trace.count('SITE EXEC')==1
assert "capture('after-preservation')" not in trace and "Qqemu.PhyMemMode:1" not in trace
assert trace.index("name='actual_xromwell_xbe_entry'")<trace.index('  preservation_experiment()')
f=read(k/'fixture-preserve001.json');seed=read(k/'fixture-seed001.json');assert sha(Path(seed['fixture_path_windows']))==seed['seed_sha256']==f['seed_sha256']
assert not f['inherited_null_policy'] and f['files']==seed['files'] and f['protected']==seed['protected']
assert not (k/'preserve001/runner-start.json').exists() and not (k/'preserve001/host-state.json').exists()
assert not Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase242-runs/nt5-phase242-preserve001').exists()
exe=k/'artifacts/build004/xemu-inventory242.exe';assert sha(exe)==build['executable_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
dest.write_text(json.dumps(dict(passed=True,executable_sha256=sha(exe),source_sha256=sha(Path(__file__)),fresh_case='preserve001',native_files=f['files'],frozen_pins=len(read(k/'emulator-frozen.json')),gpu_ownership=False,physical_access=False,guest_launch=False),indent=2)+'\n',encoding='utf-8')
print('242 compiled lock/publication/unchanged preservation and fresh-ID review PASS')
