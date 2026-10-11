"""Exact compiled sources, lock scope and preservation limitations; no guest PASS."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build004.json');assert b['passed'] and b['borrowed_sources_restored'];src=k/'artifacts/build004/source';prior=k.parent/'frontend-close246/artifacts/build001/source'
pins=read(k/'candidate004-source-pins.json')
for n in ['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/nv2a.h','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/surface.c','ui/xemu.c']:assert sha(src/n)==pins[n]
for n in ['hw/xbox/nv2a/pgraph/pgraph.c','hw/xbox/nv2a/pgraph/gl/display.c','system/physmem.c']:assert sha(src/n)==sha(prior/n)
worker=(k/'worker.c').read_text();renderer=(src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text();assert worker in renderer
assert worker.index('qemu_mutex_unlock(&d->pfifo.lock);')<worker.index('worker247_context(d,0,g_nv2a_context_render)')<worker.index('qemu_mutex_lock(&d->pfifo.lock);')
assert worker.index('if (graph) {qemu_mutex_unlock(&pg->lock);}')<worker.index('worker247_context(d,0,g_nv2a_context_render)')
assert worker.index('if (renderer) {qemu_mutex_unlock(&pg->renderer_lock);}')<worker.index('worker247_context(d,0,g_nv2a_context_render)')
assert 'qemu_mutex_trylock' in worker and 'qemu_cond_timedwait' in worker and 'pg->renderer_switch_phase!=PGRAPH_RENDERER_SWITCH_PHASE_IDLE' in worker
assert not any(t in worker for t in ['glDeleteBuffers','glDeleteTextures','glDeleteProgram','qemu_thread_join','surface_download','pgraph_gl_surface_invalidate'])
fifo=(src/'hw/xbox/nv2a/pfifo.c').read_text();a=fifo.index('if (pgraph_gl_worker247(d))');assert a<fifo.index('pgraph_process_pending(d);',a)<fifo.index('pfifo_run_pusher(d, NULL);',a)
assert 'continue;' in fifo[a:fifo.index('pgraph_process_pending(d);',a)]
assert 'G_STATIC_ASSERT(offsetof(NV2AState, parent_obj) == 0);' in (src/'hw/xbox/nv2a/nv2a_int.h').read_text()
surface=(src/'hw/xbox/nv2a/pgraph/gl/surface.c').read_text();assert surface.count('trace_nv2a_lifecycle244(82,')==1 and '// pgraph_gl_surface_download_if_dirty(d, s);' in surface
assert 'xwn_frontend246_closed' in (src/'ui/xemu.c').read_text()
tests=read(k/'worker-test003.json');assert tests['passed'] and tests['renderer_sha256']==sha(src/'hw/xbox/nv2a/pgraph/gl/renderer.c') and all(v['exit_code']==0 and not v['stderr'] for v in tests['runs'])
assert sha(src.parent/'xemu-worker247.exe')==b['executable_sha256']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),compiled_sha256=b['executable_sha256'],borrowed_sources_restored=True,source_pins={n:sha(src/n) for n in b['changed_sources']},fence_waits_outside_actor_locks=True,finite_park=True,no_new_disposal=True,natural_invalidation_coverage='flush_surfaces only; zero observed rows in247',latest_dirty_gpu_bytes_preserved_at_invalidation=False,shader_save_threads_joined=False,full_reference_retirement=False,native_gpu_ownership=False,physical_access=False),indent=2)+'\n')
print('247 exact compiled lock/no-disposal/source review PASS')
