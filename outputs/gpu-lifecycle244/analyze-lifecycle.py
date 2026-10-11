"""One actual CLOSED raw-log analysis; never replay or recollect the guest."""
import hashlib,json
from pathlib import Path
from lifecycle import parse
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'preserve001';dest=out/'lifecycle.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase244-runs/nt5-phase244-preserve001')
assert read(out/'host-state.json')['closed'] and read(run/'host-exit.json')['passed']
t=read(out/'trace.json');assert t['closed'] and not t['remaining_breakpoints']
p=run/'cpu-trace.log';data=p.read_bytes()
r=dict(passed=False,closed=True,raw_path=str(p),raw_bytes=len(data),raw_sha256=sha(p),parser_sha256=sha(k/'lifecycle.py'),trace_sha256=sha(out/'trace.json'),physical_access=False,ordinary_qualified=False)
try:
 ranges=[(v[0],v[1]) for v in t['phase_snapshot']['tuple']['surfaces']]
 r['result']=parse(data,ranges);r['passed']=True
except Exception as exc:r['error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({key:r[key] for key in ['passed','raw_bytes','error'] if key in r}))
