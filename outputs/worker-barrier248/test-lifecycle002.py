"""Execute actual parser; missing completion and cross-actor fences cannot pass."""
import copy,hashlib,json
from pathlib import Path
from lifecycle247 import parse
k=Path(__file__).resolve().parent;dest=k/'lifecycle-test002.json';assert not dest.exists()
rows=[];clock=0
def add(f,p,t=1,ref=7,a=100,b=64,stopped=0):
 global clock
 clock+=1
 tail=f'addr={a} len={b} stopped={stopped}' if f=='cpu' else f'a={a} b={b}'
 rows.append(f'{"xwn_mem_callback244" if f=="cpu" else "nv2a_lifecycle244"} phase={p} when={clock} thread={t} ref={ref} {tail}')
def data(lines):return ('\n'.join(lines)+'\n').encode()
add('cpu',1);add('nv',1,t=2)
add('cpu',2);add('nv',41,t=3,ref=0)
add('nv',10,t=4);add('nv',11,t=4,ref=11);add('nv',30,t=4,ref=11,a=0);add('nv',31,t=4,ref=11,a=0);add('nv',12,t=4);add('nv',32,t=4,ref=11,a=0)
add('nv',4,t=2);add('nv',2,t=2);add('cpu',3,t=2);add('cpu',4,stopped=1);add('nv',3,t=2);add('nv',5,t=2);add('cpu',5,stopped=1);add('nv',42,t=3,ref=0)
base=rows.copy();r=parse(data(base),[(100,64)]);assert r['target_callback_retirement_observed'] and r['observed']['complete_frontend_loans']==1 and r['observed']['cpu_stopped_frees']==1
checks=3
# Producer may queue removal before CPU insertion executes.
v=base.copy();row=v.pop(2);v.insert(v.index(next(x for x in v if 'xwn_mem_callback244 phase=4 ' in x)),row)
# Its clocks still represent original times; per-CPU execution order remains valid.
assert parse(data(v),[(100,64)])['target_callback_retirement_observed'];checks+=1
for phase in [3,4,5]:
 v=[line for line in base if not line.startswith(f'xwn_mem_callback244 phase={phase} ')]
 try:r=parse(data(v),[(100,64)])
 except AssertionError:checks+=1
 else:assert not r['target_callback_retirement_observed'];checks+=1
# New allocation can reuse scalar pointer after unlink/free but before old free log.
rows=base[:16];clock=100
add('cpu',1,t=2,a=200,b=32);add('cpu',5,stopped=1)
add('nv',42,t=3,ref=0)
r=parse(data(rows),[(100,64)]);assert r['targets'][0]['free']['addr']==100 and r['callbacks'][1]['addr']==200 and r['target_callback_retirement_observed'];checks+=3
for v in [
 [x.replace('thread=4','thread=9') if x.startswith('nv2a_lifecycle244 phase=31 ') else x for x in base],
 [x for x in base if not x.startswith('nv2a_lifecycle244 phase=31 ')],
 [x for x in base if not x.startswith('nv2a_lifecycle244 phase=42 ')],
 base+['nv2a_lifecycle244 phase=41 when=200 thread=3 ref=0 a=0 b=0'],
 base+['xwn_mem_callback244 phase=5 when=201 thread=1 ref=7 addr=100 len=64 stopped=1'],
 base+['nv2a_lifecycle244 malformed'],
]:
 try:parse(data(v),[(100,64)])
 except AssertionError:checks+=1
 else:raise AssertionError('Malformed/missing/cross-actor evidence accepted')
for blob in [data(base)[:-1],b'x'*(16*1024**2+1)]:
 try:parse(blob,[(100,64)])
 except AssertionError:checks+=1
 else:raise AssertionError('Incomplete/oversize accepted')
v=[x for x in base if not x.startswith('nv2a_lifecycle244 phase=32 ')]
r=parse(data(v),[(100,64)]);assert len(r['partial_frontend_loans'])==1 and not r['display_quiescence'];checks+=2
dest.write_text(json.dumps(dict(passed=True,checks=checks,parser_sha256=hashlib.sha256((k/'lifecycle246.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),guest_launch=False,physical_access=False),indent=2)+'\n')
print('244 causal lifecycle checks',checks)
