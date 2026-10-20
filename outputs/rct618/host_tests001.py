"""Retail integration gates and independent counter rejection cases."""
import copy,hashlib,json
from pathlib import Path
from counter_oracle import costs
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (K/'window.h').read_bytes()==(K.parent/'rct617/window.h').read_bytes()
assert (K/'timing.h').read_bytes()==(K.parent/'rct617/timing.h').read_bytes()
assert (K/'alignment_oracle.py').read_text()==(K.parent/'rct617/cost_oracle.py').read_text().split('def analyze(')[0]
for n in ['calls.h','phase.h','lifetime.h','dib_header.h','trace_oracle.py','dib_oracle.py']:
 assert (K/n).read_bytes()==(K.parent/'rct617'/n).read_bytes(),n
counter=(K/'cost.h').read_text();prior=(K.parent/'rct615/cost.h').read_text()
assert prior[:prior.index('static SNAP cost_samples[512];')].replace('xwn615','xwn618') in counter
runner=(K/'runner.c').read_text();trace=(K/'trace.c').read_text();inp=(K/'input.h').read_text()
assert 'gamepid=0;}' in runner and 'cost_identity(pi.hProcess,pi.dwProcessId)' in runner
assert 'tracehandle=pi.hProcess' in runner and 'gamehandle=pi.hProcess' not in runner
assert 'DEBUG_ONLY_THIS_PROCESS,0,"C:\\\\xwn618-kit\\\\game",' in trace
assert 'window617(gamehandle,tracehandle,request,ack,1,&n)' in (K/'retail_cost.h').read_text()
assert 'cost_game()' in inp and 'parkphase606()' not in inp
assert 'Sleep(5000);' in inp and 'capture("park-loaded-stable")' in inp
assert 'GetTickCount()-started>360000||count>10000' in trace
def row(tag,case,index,tick,cpu=0):
 return f'{tag} {case} {index} {tick*10000:016x} {tick} 0000000000000000 {cpu:016x} 8388608 8388608 8388608'
lines=['FREQ 0000000000989680',row('SLEEP_START',0,0,1000),row('SLEEP_END',0,0,6000),'SLEEP_DONE','IDENTITY 1 12 20 30 40 50']
for role in ['SUBJECT','TRACER','OBSERVER']:
 lines += [row(role+'_START',1,0,10000),row(role+'_END',1,0,30000,1000000)]
 if role!='OBSERVER':lines += [row(role+'_SAMPLE',1,i,10100+i*100,5000*(i+1)) for i in range(200)]
lines+=['SAMPLES 200','COST_DONE'];log='\n'.join(lines)
host=dict(connected=True,closed=True,clock='time.monotonic_ns',rows=[
 dict(case=c,kind=k,tick=t,monotonic_ns=t*1000000) for c,k,t in [
 (0,'START',1000),(0,'END',6000),(1,'START',10000),(1,'END',30000)]])
assert costs(log,host)[0]['1']['roles']['TRACER']['cpu_seconds']==.1
bad=[
 ('same_process',log.replace('12 20 30','12 12 30'),host),
 ('missing_recorder',log.replace('12 20 30','12 0 30'),host),
 ('missing_observer',log.replace('12 20 30','12 20 0'),host),
 ('no_completion',log.replace('COST_DONE','FAILED'),host),
 ('wrong_count',log.replace('SAMPLES 200','SAMPLES 199'),host),
 ('counter_regression',log.replace(row('SUBJECT_END',1,0,30000,1000000),row('SUBJECT_END',1,0,30000,1)),host),
 ('impossible_cpu',log.replace(row('TRACER_END',1,0,30000,1000000),row('TRACER_END',1,0,30000,900000000)),host)]
for name,mutate in [
 ('host_clock_drift',lambda h:h['rows'][3].update(monotonic_ns=35000000000)),
 ('wrong_marker',lambda h:h['rows'][2].update(tick=10001)),
 ('reader_error',lambda h:h.update(error='truncated')),
 ('missing_marker',lambda h:h['rows'].pop())]:
 h=copy.deepcopy(host);mutate(h);bad.append((name,log,h))
rejected=[]
for name,l,h in bad:
 try:costs(l,h)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,
 exact617_window_timing_alignment=True,sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h']},
 scope='Host integration and negative gates; actual617 prerequisite and618 run still required.'),indent=2)+'\n')
print('618 integration passed',len(rejected),'counter rejections')
