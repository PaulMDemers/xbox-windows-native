"""247 failed early, lacks final loader marker: qualify ONLY actual worker span."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;o=k/'preserve001';dest=o/'worker-partial002.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(o/'trace.json');assert t['closed'] and not t['passed'] and read(o/'host-state.json')['closed']
raw=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase247-runs/nt5-phase247-preserve001/cpu-trace.log');data=raw.read_bytes()
def events_only(data,ranges):
 assert not ranges and len(data)<=16*1024**2 and data.endswith(b'\n')
 out=[]
 for line_no,line in enumerate(data.decode('utf-8').splitlines()):
  if not line.startswith('nv2a_lifecycle244 '):continue
  m=re.fullmatch(r'nv2a_lifecycle244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) a=(\d+) b=(\d+)',line);assert m,line
  row=dict(zip(['phase','when','thread','ref','a','b'],map(int,m.groups())),family='nv',ordinal=line_no);assert row['thread']>0;out.append(row)
 assert len(out)<100000
 return dict(events=out)
# Actual worker qualifier uses only events, not global callback/loader pairing.
# Supply strict event-only decoding explicitly; do NOT invent a final marker.
tree=ast.parse((k/'worker.py').read_text());ns=dict(re=re,parse=events_only)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),str(k/'worker.py'),'exec'),ns)
r=dict(passed=False,scope='FAILED247 overall; partial raw worker/UI interval only. Missing final loader marker prevents complete lifecycle qualification.',trace_failed=True,ordinary_qualified=False,physical_access=False,native_gpu_ownership=False,raw_sha256=sha(raw),worker_qualifier_sha256=sha(k/'worker.py'),source_sha256=sha(Path(__file__)))
try:
 r['worker']=ns['qualify'](data,t['worker_closed_report'],t['worker_closed_reread'],t['worker_released_report']);r['worker_checkpoint_scope_passed']=True
 r['cleanup_ui_acknowledged']=t['frontend_failure_reopen_acknowledged'];assert r['cleanup_ui_acknowledged'] and t['guest_resumed'] and not t['remaining_breakpoints']
except Exception as exc:r['scope_error']=repr(exc)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','worker_checkpoint_scope_passed','worker','scope_error'] if n in r},indent=2))
