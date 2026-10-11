"""Closed248 barrier PASS is distinct from failed startup/workload/shutdown."""
import hashlib,json
from pathlib import Path
from worker import qualify
from closed import qualify as uiqualify
from lifecycle247 import parse
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'diagnostic-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
o=k/'preserve001';r=read(o/'worker.json');t=read(o/'trace.json');a=read(o/'audit.json');m=read(k/'matrix001.json')
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase248-runs/nt5-phase248-preserve001');raw=run/'cpu-trace.log';data=raw.read_bytes()
assert m['completed'] and m['closed'] and read(o/'host-state.json')['closed'] and read(run/'host-exit.json')['passed']
assert not r['passed'] and r['raw_sha256']==sha(raw) and t['passed'] and t['worker_scope_passed'] and t['frontend_scope_passed'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert qualify(data,t['worker_closed_report'],t['worker_closed_reread'],t['worker_released_report'])==r['worker']
assert uiqualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_reopened_report'])==r['frontend']
full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]);private=Path(r['full_analysis']['path']);assert sha(private)==r['full_analysis']['sha256'] and read(private)==full
assert full['target_callback_retirement_observed'] and full['observed']['cpu_stopped_frees']==0 and not full['observed']['sync_null_returns']
assert a['integrity_passed'] and not a['cpu_scope_passed'] and not a['guest_trace_scope_passed'] and a['normal_shutdown_count']==0 and not a['dashboard_return']
assert not a['workload']['passed'] and not a['wizard']['passed'] and not a['retirement']['passed']
assert not a['strict_events_passed'] and not a['strict_qualification_passed'] and not a['ordinary_qualified'] and not a['physical_qualified']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49 and not a['new_events']['application']
wizard=o/'artifacts/wizard201.log';log=wizard.read_text();assert 'TIMEOUT201 1 0 120210' in log and 'INSTALL_STATE 258 119955 0' in log
assert not (o/'artifacts/result.log').exists() and not (o/'artifacts/retirement.log').exists()
runtime=read(run/'runtime-checkpoint001.json');assert runtime['status']=='shell_running' and runtime['bugcheck_data']==['0x0']*5
prior=read(k.parent/'worker-barrier247/preserve001/worker-partial002.json');assert not prior['passed'] and prior['trace_failed']
src=k/'artifacts/build004/source';b=read(k/'parent001.json');assert sha(src.parent/'xemu-worker247.exe')==b['executable_sha256']
assert read(k.parent/'worker-barrier247/source-review001.json')['passed']
dest.write_text(json.dumps(dict(review_passed=True,overall_run_passed=False,barrier_scope_passed=True,source_sha256=sha(Path(__file__)),raw_sha256=sha(raw),wizard_sha256=sha(wizard),frozen_pins=len(read(k/'emulator-frozen.json')),actual_emulator_sha256=b['executable_sha256'],worker=r['worker'],frontend=r['frontend'],observed=full['observed'],integrity_passed=True,normal_shutdown_count=0,dashboard_return=False,workload_started=False,setup_timeout_ms=120210,pending_install_wait_result=258,strict_qualified=False,ordinary_qualified=False,physical_qualified=False,native_gpu_ownership=False,prior247_remains_failed=True),indent=2)+'\n')
print('248 raw barrier reviewed PASS; inherited setup timeout/workload/shutdown/strict gates remain FAIL')
