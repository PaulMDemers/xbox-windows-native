"""Reject timing, identity, sample, memory and source-inheritance defects."""
import copy,hashlib,json
from pathlib import Path
from cost_oracle import analyze
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'host-tests001.json';assert not out.exists()
old=(K.parent/'rct614/sampler.c').read_text();new=(K/'cost.h').read_text()
for start,end in [('static ULONGLONG ft','static BOOL text('),
                  ('static BOOL mark','void WINAPI mainCRTStartup(void)')]:
 piece=old[old.index(start):old.index(end)]
 assert piece in new,start
runner=(K/'runner.c').read_text();inp=(K/'input.h').read_text()
assert 'gamehandle=pi.hProcess' in runner and '"cost.h"' in runner and '<psapi.h>' in runner
assert 'CreateProcessA("C:\\\\xwn615-kit\\\\game\\\\RCT.EXE",cmd,0,0,FALSE,0,0,game,&si,&pi)' in runner
assert not any(v in runner for v in ['DEBUG_PROCESS','trace615','debugger_pid'])
assert 'parkphase606' not in inp and 'park_verified||!state("cost-before")' in inp
assert 'cost_game()' in inp and 'state("cost-after")' in inp
interval=new[new.index(' do{',new.index('static BOOL cost_game')):new.index(' if(!snap(gamehandle,&b')]
assert 'WaitForSingleObject(gamehandle,100)' in interval and 'n>=512' in interval
assert not any(v in interval for v in ['text(','row(','WriteFile','capture(','SendInput','state('])
assert 'and not serial.lines.rows:' in (K/'vm.py').read_text()
def row(tag,case,index,tick,cpu):
 return f'{tag} {case} {index} {tick*10000:016x} {tick} 0000000000000000 {cpu:016x} 8388608 8388608 8388608'
lines=['FREQ 0000000000989680',row('SLEEP_START',0,0,1000,0),row('SLEEP_END',0,0,6000,0),'SLEEP_DONE',
 row('GAME_START',1,0,10000,0),row('GAME_END',1,0,30000,100000000),
 row('OBSERVER_START',1,0,10000,0),row('OBSERVER_END',1,0,30000,156250)]
lines += [row('SAMPLE',1,i,10100+i*100,(i+1)*500000) for i in range(200)]
lines+=['SAMPLES 200','COST_DONE'];log='\n'.join(lines)
host=dict(connected=True,closed=True,clock='time.monotonic_ns',rows=[
 dict(case=c,kind=k,tick=t,monotonic_ns=t*1000000) for c,k,t in [(0,'START',1000),(0,'END',6000),(1,'START',10000),(1,'END',30000)]])
assert analyze(log,host)['game']['cpu_seconds']==10
variants={}
def mutate(name,fn):
 h=copy.deepcopy(host);fn(h);variants[name]=(log,h)
mutate('host_clock_drift',lambda h:h['rows'][3].update(monotonic_ns=32000000000))
mutate('wrong_case',lambda h:h['rows'][2].update(case=0))
mutate('wrong_tick',lambda h:h['rows'][2].update(tick=10001))
mutate('missing_marker',lambda h:h['rows'].pop())
mutate('coalesced_markers',lambda h:h['rows'][3].update(monotonic_ns=10000000000))
mutate('reader_error',lambda h:h.update(error='partial line'))
mutate('reader_open',lambda h:h.update(closed=False))
variants['counter_regression']=(log.replace(row('GAME_END',1,0,30000,100000000),row('GAME_END',1,0,30000,1)),host)
variants['impossible_cpu']=(log.replace(row('GAME_END',1,0,30000,100000000),row('GAME_END',1,0,30000,900000000)),host)
variants['missing_sample']=(log.replace(row('SAMPLE',1,12,11300,6500000),'').replace('\n\n','\n'),host)
variants['duplicate_sample']=(log.replace('SAMPLES 200',row('SAMPLE',1,199,30000,100000000)+'\nSAMPLES 201'),host)
variants['zero_memory']=(log.replace('8388608 8388608 8388608','0 8388608 8388608',1),host)
variants['missing_completion']=(log.replace('COST_DONE',''),host)
rejected=[]
for name,(l,h) in variants.items():
 try:analyze(l,h)
 except (AssertionError,ValueError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,source_inheritance=True,
 sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py']},
 scope='Host arithmetic/guards/inheritance only; no game result.'),indent=2)+'\n')
print('615 host tests:',len(rejected),'negative outcomes passed')
