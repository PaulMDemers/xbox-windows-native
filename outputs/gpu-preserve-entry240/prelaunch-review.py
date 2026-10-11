"""Review new scope/guards and unchanged actual compiled preservation producer."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in read(k/'emulator-frozen.json').items():assert sha(ws/path)==digest,path
t=read(k/'preservation-test003.json');assert t['passed'] and t['actual_trace_source_sha256']==sha(k/'trace.py')
for name in ['host-close','connection']:assert read(k/(name+'-test001.json'))['passed']
guard=read(k/'guard-test002.json');assert guard['passed'] and guard['source_sha256']==sha(k/'trace.py')
compiled=k.parent/'gpu-reference-snapshot238/artifacts/build001/source/hw/xbox/nv2a'
nv=(compiled/'nv2a.c').read_text(encoding='utf-8');renderer=(compiled/'pgraph/gl/renderer.c').read_text(encoding='utf-8');surface=(compiled/'pgraph/gl/surface.c').read_text(encoding='utf-8')
setter=nv[nv.index('static void preserve227_set'):nv.index('static char *preserve227_report')]
assert setter.index('qemu_mutex_trylock')<setter.index('d->preserve227.old_halt')<setter.index('qatomic_set(&d->pfifo.halt, true)')<setter.index('qatomic_store_release(&d->preserve227.state, 1)')
fn=surface[surface.index('unsigned pgraph_gl_preserve227'):surface.index('void pgraph_gl_process_pending_downloads')]
assert 'memcmp(expected, d->vram_ptr + s->vram_addr, s->size)' in fn
assert 'surface_download_to_buffer(d, s, true, false, true, expected)' in fn and 'surface_download(d, s, true)' in fn
assert fn.count('preserve227_fence(d)')==2 and 'return 3;' in fn
assert 'QTAILQ_REMOVE' not in fn and 'surface_invalidate(' not in fn and 'flush_surfaces(' not in fn
worker=renderer[renderer.index('    if (qatomic_load_acquire(&d->preserve227.state) == 1)'):renderer.index('    if (qatomic_read(&r->downloads_pending)')]
assert worker.index('qemu_mutex_unlock(&d->pfifo.lock)')<worker.index('qemu_mutex_lock(&pg->lock)')
assert 'nv2a_preserve227_finish(d, result)' in worker
finish=nv[nv.index('void nv2a_preserve227_finish'):nv.index('/*238 ONE request')]
assert 'result == 3 || result == 4' in finish and 'd->preserve227.old_halt' in finish
trace=(k/'trace.py').read_text(encoding='utf-8');assert trace.count("qom-set '+path+' xwn-preserve227 true")==1 and trace.count('SITE EXEC')==1
assert "if case=='preserve001':" in trace and 'unknown_or_unsafe_terminal_quarantined' in trace
assert trace.index("name='actual_xromwell_xbe_entry'")<trace.index('  preservation_experiment()')
assert "Qqemu.PhyMemMode:1" not in trace and "arm(2," not in trace
seed=read(k/'fixture-seed001.json');fixtures=[]
control=read(k.parent/'gpu-preserve-entry239/control001/closure.json');assert control['cpu_scope_passed'] and control['guest_trace_scope_passed']
assert sha(k.parent/'gpu-preserve-entry239/control001/audit.json')==control['audit_sha256']
assert read(k.parent/'gpu-preserve-entry239/fixture-control001.json')['seed_sha256']==seed['seed_sha256']
for case in ['preserve001']:
 f=read(k/('fixture-'+case+'.json'));assert f['phase']=='xbe' and f['files']==seed['files'] and f['protected']==seed['protected'] and not f['inherited_null_policy']
 assert not (k/case/'runner-start.json').exists() and not (k/case/'host-state.json').exists()
 fixtures.append(dict(case=case,immutable_seed_sha256=f['seed_sha256']))
assert sha(Path(seed['fixture_path_windows']))==seed['seed_sha256']
exe=k.parent/'gpu-reference-snapshot238/artifacts/build001/xemu-reference238.exe';assert sha(exe)==read(k.parent/'gpu-reference-snapshot238/build001.json')['executable_sha256']
record=dict(passed=True,fixtures=fixtures,executable_sha256=sha(exe),source_sha256=sha(Path(__file__)),compiled_review={p.relative_to(compiled).as_posix():sha(p) for p in [compiled/'nv2a.c',compiled/'pgraph/gl/renderer.c',compiled/'pgraph/gl/surface.c',compiled/'pfifo.c']},scope='Unchanged compiled232 worker in238: one new preservation at actual Xromwell; full fence/byte comparison, references retained; no native ownership',physical_access=False,guest_launch=False)
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('239 prelaunch review PASS')
