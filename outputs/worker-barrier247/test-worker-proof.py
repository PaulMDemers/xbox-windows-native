"""Bounded actual parser positive/negative proof; synthetic adapter not runtime."""
import hashlib,json
from pathlib import Path
from worker import qualify
from lifecycle247 import parse
k=Path(__file__).resolve().parent;dest=k/'worker-proof001.json';assert not dest.exists()
raw=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase246-runs/nt5-phase246-preserve001/cpu-trace.log');data=raw.read_bytes();e=parse(data,[])['events']
ack=next(x for x in e if x['family']=='nv' and x['phase']==61);boundary=next(x for x in e if x['family']=='nv' and x['phase']==63)
time=ack['when']+1000;lines=[]
def event(phase,ref,a,b,when=None,thread=555):
 global time
 time+=1000
 lines.append(f'nv2a_lifecycle244 phase={phase} when={time if when is None else when} thread={thread} ref={ref} a={a} b={b}\n')
event(70,0,1,0,thread=444);event(71,0,2,0);event(76,123,4096,8192);event(77,123,42,0)
for n in range(2):
 for j in range(7):event(73,n*7+j,13,100+n)
 event(74,n,100000000,0);event(75,n,0x911c,0)
event(78,0,3,0);event(80,0,5,0,when=time+220000000)
assert time+220000000<boundary['when']
parts=data.splitlines(keepends=True);idx=boundary['line']-1;base=b''.join(parts[:idx])+''.join(lines).encode()+b''.join(parts[idx:])
r='version=247 state=3 ready=1 reason=0 count=1 dirty=0 error=0 when=123 thread=555 context0=100 context1=101 fence0=37148 fence1=37148 '+' '.join(f'binding{i}=13' for i in range(14))+' '+' '.join(f'surface0_{j}={v}' for j,v in enumerate([123,4096,8192,42,0,1]))
checks=0
def run(d,a=r,b=None,c=None,pass_expected=False):
 global checks
 try:qualify(d,a,a if b is None else b,a.replace('state=3 ','state=5 ') if c is None else c)
 except (AssertionError,KeyError):assert not pass_expected
 else:assert pass_expected
 checks+=1
run(base,pass_expected=True)
for old,new in [('fence0=37148','fence0=37147'),('dirty=0','dirty=1'),('reason=0','reason=5'),('context1=101','context1=100'),('surface0_4=0','surface0_4=1'),('thread=555','thread=999')]:run(base,r.replace(old,new))
run(base,b=r+' binding99=0');run(base,c=r)
run(base.replace(lines[-1].encode(),b''));run(base.replace(lines[-1].encode(),lines[-1].replace('a=5','a=6').encode()))
run(base.replace(lines[0].encode(),lines[0].encode()*2))
run(base.replace(lines[-2].encode(),lines[-2].encode()+b'nv2a_lifecycle244 phase=4 when=123 thread=555 ref=0 a=0 b=0\n'))
run(base.replace(lines[-1].encode(),lines[-1].replace(str(time+220000000),str(time+1000000)).encode()))
dest.write_text(json.dumps(dict(passed=True,checks=checks,parser_sha256=hashlib.sha256((k/'worker.py').read_bytes()).hexdigest(),prior_raw_sha256=hashlib.sha256(data).hexdigest(),scope='Synthetic worker events inserted into actual246 log; parser adapters only, no247 guest proof',guest_launch=False,physical_access=False),indent=2)+'\n')
print('247 parser refusal/omission/actor/park guards PASS',checks)
