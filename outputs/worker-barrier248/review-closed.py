"""Independent raw/checkpoint/complete lifecycle and cold source review."""
import hashlib,json
from pathlib import Path
from worker import qualify
from closed import qualify as uiqualify
from lifecycle247 import parse
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
o=k/'preserve001';r=read(o/'worker.json');t=read(o/'trace.json');a=read(o/'audit.json');m=read(k/'matrix001.json')
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase248-runs/nt5-phase248-preserve001');raw=run/'cpu-trace.log';data=raw.read_bytes()
assert m['completed'] and m['closed'] and read(o/'host-state.json')['closed'] and read(run/'host-exit.json')['passed']
assert r['passed'] and r['raw_sha256']==sha(raw) and t['passed'] and t['worker_scope_passed'] and t['frontend_scope_passed'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert qualify(data,t['worker_closed_report'],t['worker_closed_reread'],t['worker_released_report'])==r['worker']
assert uiqualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_reopened_report'])==r['frontend']
full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]);private=Path(r['full_analysis']['path']);assert sha(private)==r['full_analysis']['sha256'] and read(private)==full
assert full['target_callback_retirement_observed'] and full['observed']['cpu_stopped_frees']==0 and not full['observed']['sync_null_returns']
assert a['cpu_scope_passed'] and a['guest_trace_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
assert not a['strict_events_passed'] and not a['strict_qualification_passed'] and not a['ordinary_qualified'] and not a['physical_qualified']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49 and not a['new_events']['application']
src=k/'artifacts/build004/source';assert sha(src.parent/'xemu-worker247.exe')==read(k/'parent001.json')['executable_sha256']
helper=(k/'worker.c').read_text();assert helper in (src/'hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
assert 'qemu_cond_timedwait(&d->pfifo.fifo_cond,&d->pfifo.lock,20)' in helper
assert '100000000' in helper and 'glDeleteSync(fence)' in helper and not any(x in helper for x in ['glDeleteTextures','glDeleteBuffers','glDeleteProgram','pgraph_gl_surface_invalidate','surface_download'])
assert 'bool xwn_frontend246_closed(void)' in (src/'ui/xemu.c').read_text()
prior=read(k.parent/'worker-barrier247/preserve001/worker-partial002.json');assert not prior['passed'] and prior['trace_failed'] and not read(k.parent/'worker-barrier247/matrix001.json')['completed']
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),raw_sha256=sha(raw),frozen_pins=len(read(k/'emulator-frozen.json')),actual_emulator_sha256=read(k/'parent001.json')['executable_sha256'],worker=r['worker'],frontend=r['frontend'],observed=full['observed'],integrity_passed=True,strict_qualified=False,ordinary_qualified=False,physical_qualified=False,native_gpu_ownership=False,prior247_remains_failed=True),indent=2)+'\n')
print('248 actual raw/source/context/park/strict-failure/cold review PASS')
