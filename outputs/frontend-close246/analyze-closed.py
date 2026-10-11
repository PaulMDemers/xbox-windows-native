"""Once-only cold246 close/reopen qualification from raw pinned event log."""
import hashlib,json
from pathlib import Path
from closed import qualify
from lifecycle246 import parse
k=Path(__file__).resolve().parent;out=k/'preserve001';dest=out/'frontend.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase246-runs/nt5-phase246-preserve001');state=read(out/'host-state.json');assert state['closed'] and read(run/'host-exit.json')['passed']
t=read(out/'trace.json');assert t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['lifecycle_window_closed']
raw=run/'cpu-trace.log';data=raw.read_bytes();r=dict(passed=False,closed=True,raw_path=str(raw),raw_sha256=sha(raw),raw_bytes=len(data),source_sha256=sha(Path(__file__)),protocol_parser_sha256=sha(k/'closed.py'),lifecycle_parser_sha256=sha(k/'lifecycle246.py'),physical_access=False,ordinary_qualified=False,native_gpu_ownership=False)
try:
 assert t['passed'] and t.get('frontend_scope_passed')
 r['frontend']=qualify(data,t['frontend_closed_report'],t['frontend_closed_reread'],t['frontend_reopened_report'])
 full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]);private=out/'artifacts/lifecycle-full246.json';assert not private.exists();private.write_text(json.dumps(full,indent=2)+'\n')
 r['full_analysis']=dict(path=str(private.resolve()),sha256=sha(private),bytes=private.stat().st_size)
 r['observed']=full['observed'];r['target_callback_retirement_observed']=full['target_callback_retirement_observed'];r['marker_loans']=[len(v['frontend_inflight']) for v in full['marks']]
 r['targets']=full['targets']
 a=read(out/'audit.json');r['cpu_scope_passed']=a['cpu_scope_passed'];r['integrity_passed']=a['integrity_passed'];r['strict_events_passed']=a['strict_events_passed'];r['warnings_errors']=a['warnings_errors'];r['normal_shutdown_count']=a['normal_shutdown_count']
 assert r['frontend']['passed'] and a['cpu_scope_passed'] and a['guest_trace_scope_passed'] and full['target_callback_retirement_observed']
 r['passed']=True
except Exception as exc:r['error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','frontend','observed','error'] if n in r},indent=2))
