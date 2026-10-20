"""Exact qualified sampling inheritance and retail log rejection checks."""
import copy,hashlib,json
from pathlib import Path
from cost_oracle import analyze
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=(K.parent/'rct620/runner.c').read_text();new=(K/'profile.h').read_text()
assert (K/'suspend.h').read_bytes()==(K.parent/'rct620/suspend.h').read_bytes()
for a,b in [('typedef BOOL (WINAPI *ENUMFN)','static BOOL run('),(' while(GetTickCount()-a.tick<20000)',' if(!SetEvent(release)')]:
 piece=old[old.index(a):old.index(b)].replace('static BOOL modules(','static BOOL profile_modules(').replace('modules(pi.hProcess','profile_modules(pi.hProcess')
 assert piece in new,a
assert 'CreateProcessA("C:\\\\xwn621-kit\\\\game\\\\RCT.EXE"' in (K/'runner.c').read_text()
assert 'gamethread=pi.hThread;gametid=pi.dwThreadId' in (K/'runner.c').read_text()
assert 'restored=SetThreadPriority(GetCurrentThread(),priority)' in (K/'cost.h').read_text()
for name in ['input.h','game_capture.h','park_reference.h','load_dialog002.h','title_signature.h','welcome.h','park_phase.h']:
 assert (K/name).read_text()==(K.parent/'rct615'/name).read_text().replace('xwn615','xwn621').replace('XWN615','XWN621'),name
assert json.loads((K.parent/'rct620/final001.json').read_text())['passed']
def row(tag,case,n,tick,cpu):return f'{tag} {case} {n} 0000000000000001 {tick} 0000000000000000 {cpu:016x} 1000000 1000000 1000000'
lines=['FREQ 0000000000010000',row('SLEEP_START',0,0,1000,0),row('SLEEP_END',0,0,6000,0),'SLEEP_DONE',
 'THREAD_READY 4 0000000000000001 0000000000000000 0000000000000000 0000000000000000',
 'IDENTITY 4 200 204 100 0000000000000001','MODULE 4 00400000 00010000 C:\\xwn621-kit\\game\\RCT.EXE',
 row('SUBJECT_START',4,0,10000,0),row('SUBJECT_END',4,200,30000,190000000),row('OBSERVER_START',4,0,10000,0),row('OBSERVER_END',4,200,30000,156250),
 'THREAD_START 4 0000000000000001 0000000000000000 0000000000000000','THREAD_END 4 0000000000000001 0000000000000000 000000000b532b80']
lines += [f'SAMPLE 4 {i} {10000+i*100} 00401000 00120000 00000000 0000001b 0 0 1' for i in range(200)]
lines+=['PROFILE_DONE'];log='\n'.join(lines)
host=dict(connected=True,closed=True,rows=[dict(kind=kind,case=case,tick=tick,monotonic_ns=tick*1000000) for kind,case,tick in [('START',0,1000),('END',0,6000),('START',5,10000),('END',5,30000)]])
assert analyze(log,host)['main_thread_cpu_seconds']==19
variants={}
for name,oldtext,newtext in [('completion','PROFILE_DONE',''),('identity','IDENTITY 4 200 204 100','IDENTITY 4 200 204 200'),
 ('module','00400000 00010000','00500000 00010000'),('sample-order','SAMPLE 4 1 10100','SAMPLE 4 1 10000'),
 ('sample-index','SAMPLE 4 1 10100','SAMPLE 4 2 10100'),('invalid-cs','0000001b','00000008'),('hold',' 0 0 1',' 101 0 1'),
 ('suspend',' 0 0 1',' 0 1 2'),('too-few','SAMPLE 4 199 29900 00401000 00120000 00000000 0000001b 0 0 1',''),
 ('thread-coverage','000000000b532b80','0000000000989680'),('bad-image','game\\RCT.EXE','game\\OTHER.EXE')]:variants[name]=(log.replace(oldtext,newtext),host)
for name,fn in [('host-error',lambda h:h.update(error='bad')),('host-open',lambda h:h.update(closed=False)),('host-drift',lambda h:h['rows'][3].update(monotonic_ns=32000000000)),('wrong-case',lambda h:h['rows'][3].update(case=4))]:
 h=copy.deepcopy(host);fn(h);variants[name]=(log,h)
rejected=[]
for name,(l,h) in variants.items():
 try:analyze(l,h)
 except (AssertionError,ValueError,IndexError):rejected.append(name)
 else:raise AssertionError('Accepted '+name)
out.write_text(json.dumps(dict(passed=True,rejections=rejected,qualified620_primitives_and_loop_exact=True,sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py']}),indent=2)+'\n')
print('Qualified620 loop inheritance and',len(rejected),'profile negatives passed')
