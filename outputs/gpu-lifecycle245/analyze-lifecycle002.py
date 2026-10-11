"""Once-only closed trace pairing, full evidence private and compact report public."""
import hashlib,json
from pathlib import Path
from lifecycle import parse
k=Path(__file__).resolve().parent;out=k/'preserve001';dest=out/'lifecycle.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase245-runs/nt5-phase245-preserve001')
assert read(out/'host-state.json')['closed'] and read(run/'host-exit.json')['passed']
t=read(out/'trace.json');assert t['closed'] and not t['remaining_breakpoints'] and t['lifecycle_window_closed']
p=run/'cpu-trace.log';data=p.read_bytes()
r=dict(passed=False,closed=True,raw_path=str(p),raw_bytes=len(data),raw_sha256=sha(p),parser_sha256=sha(k/'lifecycle.py'),source_sha256=sha(Path(__file__)),trace_sha256=sha(out/'trace.json'),physical_access=False,ordinary_qualified=False)
try:
 full=parse(data,[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']])
 private=out/'artifacts/lifecycle-full.json';assert not private.exists();private.write_text(json.dumps(full,indent=2)+'\n')
 r['full_analysis']=dict(path=str(private.resolve()),sha256=sha(private),bytes=private.stat().st_size)
 summary={key:value for key,value in full.items() if key not in ['events','callbacks','flushes','frontend_loans','sync_returns']}
 summary['example_frontend_loans']=full['frontend_loans'][:2]+full['frontend_loans'][-2:]
 summary['flushes']=full['flushes'];summary['callbacks_completed']=len([v for v in full['callbacks'] if v['free']])
 summary['callback_free_during_cpu_stop_observed']=any(v['free'] and v['free']['stopped'] for v in full['callbacks'])
 r['result']=summary;r['passed']=True
except Exception as exc:r['error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({key:r[key] for key in ['passed','raw_bytes','error'] if key in r}))
