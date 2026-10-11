"""Exercise actual close evidence parser including missing/racing/partial paths."""
import hashlib,json
from pathlib import Path
from closed import qualify
k=Path(__file__).resolve().parent;dest=k/'closed-test001.json';assert not dest.exists()
rows=[]
def add(p,when,t=4,ref=0,a=0,b=0):rows.append(f'nv2a_lifecycle244 phase={p} when={when} thread={t} ref={ref} a={a} b={b}')
def frame(when):
 for i,p in enumerate([10,11,30,31,12,32]):add(p,when+i,ref=11 if p in [11,30,31,32] else 0)
add(41,1,t=3);frame(10);add(60,100,t=3,a=1);add(66,101,a=11,b=100000000);add(67,102,a=0x911c)
for i in range(7):add(65,103+i,a=i,b=13)
add(61,110,a=2);add(63,200000110,t=3,a=2,b=4);add(64,200000111,a=4,b=5);frame(200000120);add(42,200000130,t=3)
report='version=246 state=2 ready=1 when=99 thread=4 context=7 loan=0 bql=0 error=0 texture=11 fallback=0 live=1 fence=37148 '+' '.join(f'binding{i}=13' for i in range(7))
reopened=report.replace('state=2 ','state=5 ')
blob=lambda v:('\n'.join(v)+'\n').encode();checks=0
def expect(v,text=report,again=report,end=reopened,passed=False):
 global checks
 try:qualify(blob(v),text,again,end);actual=True
 except (AssertionError,KeyError,ValueError):actual=False
 assert actual==passed;checks+=1
expect(rows,passed=True)
for phase in [60,61,63,64,65,66,67]:expect([x for x in rows if not x.startswith(f'nv2a_lifecycle244 phase={phase} ')])
for field in ['loan=0','bql=0','error=0','ready=1','state=2','fence=37148']:
 bad=report.replace(field,field.split('=')[0]+'=99');expect(rows,bad,bad,bad.replace('state=2','state=5'))
expect(rows,end=report);expect(rows,again=report+' changed=1')
expect([x.replace('thread=4','thread=5') if 'phase=67 ' in x else x for x in rows])
v=rows.copy();v.insert(next(i for i,x in enumerate(v) if 'phase=63 ' in x),'nv2a_lifecycle244 phase=10 when=1000 thread=9 ref=0 a=0 b=0');expect(v)
expect([x.replace('200000111','20000111') if 'phase=64 ' in x else x for x in rows])
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256((k/'closed.py').read_bytes()).hexdigest(),parser_sha256=hashlib.sha256((k/'lifecycle246.py').read_bytes()).hexdigest(),physical_access=False,guest_launch=False),indent=2)+'\n')
print('246 actual close evidence negative/positive adapters PASS',checks)
