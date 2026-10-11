"""Closed247 remains FAILED; scope actual checkpoint/cleanup separately."""
import hashlib,json
from pathlib import Path
from worker import qualify
from closed import qualify as uiqualify
from lifecycle247 import parse
k=Path(__file__).resolve().parent;o=k/'preserve001';dest=o/'worker.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase247-runs/nt5-phase247-preserve001');t=read(o/'trace.json');a=read(o/'audit.json')
assert read(o/'host-state.json')['closed'] and read(run/'host-exit.json')['passed'] and t['closed'] and not t['passed']
raw=run/'cpu-trace.log';data=raw.read_bytes();r=dict(passed=False,raw_sha256=sha(raw),source_sha256=sha(Path(__file__)),parser_sha256=sha(k/'worker.py'),trace_failed=True,physical_access=False,ordinary_qualified=False,native_gpu_ownership=False)
try:
 assert t['worker_scope_passed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['frontend_failure_reopen_acknowledged']
 r['worker']=qualify(data,t['worker_closed_report'],t['worker_closed_reread'],t['worker_released_report'])
 r['ui_abort_cleanup']=uiqualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_failure_reopen_report'])
 full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]);p=o/'artifacts/lifecycle-full247.json';assert not p.exists();p.write_text(json.dumps(full,indent=2)+'\n')
 r['full_analysis']=dict(path=str(p.resolve()),sha256=sha(p));r['observed']=full['observed'];r['target_callback_retirement_observed']=full['target_callback_retirement_observed']
 r['worker_checkpoint_scope_passed']=True
except Exception as exc:r['scope_error']=repr(exc)
for n in ['cpu_scope_passed','integrity_passed','strict_events_passed','warnings_errors','normal_shutdown_count']:r[n]=a[n]
r['actual_host_failure']=t['host_traceback'];dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','worker_checkpoint_scope_passed','worker','scope_error'] if n in r},indent=2))
