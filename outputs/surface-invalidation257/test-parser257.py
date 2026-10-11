"""Reject malformed new telemetry and activity during the closed worker interval."""
import hashlib,json
from pathlib import Path
from lifecycle257 import parse
from worker257 import qualify
k=Path(__file__).resolve().parent;o=k/'preserve001';dest=k/'parser-review257.json';assert not dest.exists()
raw=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase257-runs/nt5-phase257-preserve001/cpu-trace.log').read_bytes()
t=json.loads((o/'trace.json').read_text());args=[t[x] for x in ['worker_closed_report','worker_closed_reread','worker_released_report']]
assert qualify(raw,*args)['passed']
lines=raw.splitlines(keepends=True);part=next(x for x in lines if x.startswith(b'nv2a_lifecycle244 phase=100 '))
cases={'missing_part':raw.replace(part,b'',1),'duplicate_part':raw+part,'unknown_phase':raw+b'nv2a_lifecycle244 phase=999 when=1 thread=1 ref=0 a=0 b=0\n'}
park=next(x for x in lines if x.startswith(b'nv2a_lifecycle244 phase=78 '));v=dict(x.split(b'=') for x in park.split()[1:]);when=int(v[b'when'])+1;thread=int(v[b'thread'])
group=b''.join(f'nv2a_lifecycle244 phase={p} when={when} thread={thread} ref=999 a={2 if p==100 else 0} b=0\n'.encode() for p in range(100,107))
cases['complete_activity_while_parked']=raw.replace(park,park+group,1)
result=[]
for name,data in cases.items():
 try:qualify(data,*args)
 except (AssertionError,ValueError,KeyError) as e:result.append(dict(case=name,rejected=True,error=repr(e)))
 else:raise AssertionError('Invalid trace accepted: '+name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,positive_actual_trace=True,negative_cases=result,raw_sha256=hashlib.sha256(raw).hexdigest(),sources={n:sha(k/n) for n in ['test-parser257.py','lifecycle247.py','lifecycle257.py','worker.py','worker257.py','closed.py','closed257.py','analyze-sites.py','analyze-worker257.py']},original_worker_failure_preserved=True,physical_access=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
