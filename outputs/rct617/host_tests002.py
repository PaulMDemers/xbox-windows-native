"""Host reject cases for clocks, identities, alignment and shared timing storage."""
import copy,hashlib,json,os,subprocess
from pathlib import Path
from counter_oracle import costs
from cost_oracle import alignment
K=Path(__file__).resolve().parent;out=K/'host-tests002.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
O=Path('/mnt/c/xwn617/host002');O.mkdir(parents=True,exist_ok=False)
cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(K),str(K/'host_timing.c'),'-o',str(O/'timing')]
subprocess.run(cmd,check=True);subprocess.run([str(O/'timing')],check=True,timeout=10)
for n in ['calls.h','lifetime.h','phase.h','dib_header.h','trace_oracle.py','dib_oracle.py']:
 assert (K/n).read_bytes()==(K.parent/'rct610'/n).read_bytes(),n
sam=(K.parent/'rct614/sampler.c').read_text();counter=(K/'counter.h').read_text()
assert sam[sam.index('typedef BOOL'):sam.index('#ifdef WORKER')] in counter
assert sam[sam.index('static HANDLE serialh;'):sam.index('void WINAPI mainCRTStartup(void)')] in counter
runner=(K/'runner.c').read_text();subject=(K/'subject.c').read_text();trace=(K/'trace.c').read_text()
assert 'OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|SYNCHRONIZE,FALSE,id[0])' in runner
assert 'ct.dwLowDateTime!=id[2]||ct.dwHighDateTime!=id[3]' in runner
assert 'lstrcmpiA(image,"C:\\\\xwn617-kit\\\\subject.exe")!=0' in runner
assert 'id[1]!=pi.dwProcessId' in runner and 'id[0]==id[1]' in runner
window=(K/'window.h').read_text()
assert window.index('!mark("START"')<window.index('!SetEvent(request)')
assert window.index('!mark("END"')<window.index('row("SUBJECT_START"')
assert 'WaitForSingleObject(ack,0)' in window and 'SuspendThread' not in window
assert 'WaitForSingleObject(go,' not in subject
assert trace.index('!hit617(&timing')<trace.index('if(bp[index].api>=3&&seen')
def row(tag,case,index,tick,cpu=0):
 return f'{tag} {case} {index} {tick*10000:016x} {tick} 0000000000000000 {cpu:016x} 8388608 8388608 8388608'
lines=['FREQ 0000000000989680',row('SLEEP_START',0,0,1000),row('SLEEP_END',0,0,6000)]
for case,start in [(1,10000),(2,40000)]:
 lines.append(f'IDENTITY {case} {10+case} {20 if case==2 else 0} 30 40 50')
 for role in ['SUBJECT','OBSERVER']+(['TRACER'] if case==2 else []):
  lines += [row(role+'_START',case,0,start),row(role+'_END',case,0,start+20000,1000000)]
  if role!='OBSERVER':lines += [row(role+'_SAMPLE',case,i,start+100*(i+1),5000*(i+1)) for i in range(200)]
 lines.append(f'CASE {case} 200 0 0')
lines+=['CONTROL_PASS','RESTART'];log='\n'.join(lines)
host=dict(connected=True,closed=True,clock='time.monotonic_ns',rows=[
 dict(case=c,kind=k,tick=t,monotonic_ns=t*1000000) for c,k,t in [
 (0,'START',1000),(0,'END',6000),(1,'START',10000),(1,'END',30000),(2,'START',40000),(2,'END',60000)]])
subjects=['SUBJECT 0 PID 11 START 10000 END 30020 COPIES 195 PASS 1','SUBJECT 1 PID 12 START 40000 END 60020 COPIES 195 PASS 1']
assert costs(log,host,subjects)[0]['2']['roles']['TRACER']['cpu_seconds']==.1
variants={
 'same_process_roles':(log.replace('IDENTITY 2 12 20','IDENTITY 2 12 12'),host,subjects),
 'wrong_subject_pid':(log,host,[subjects[0],subjects[1].replace('PID 12','PID 13')]),
 'missing_recorded_process':(log.replace('IDENTITY 2 12 20','IDENTITY 2 12 0'),host,subjects),
 'failed_pixels':(log,host,[subjects[0],subjects[1].replace('PASS 1','PASS 0')]),
 'work_after_interval':(log,host,[subjects[0],subjects[1].replace('END 60020','END 90000')]),
 'missing_completion':(log.replace('CONTROL_PASS','CONTROL_FAIL'),host,subjects),
 'counter_regression':(log.replace(row('SUBJECT_END',2,0,60000,1000000),row('SUBJECT_END',2,0,60000,1)),host,subjects),
 'impossible_cpu':(log.replace(row('SUBJECT_END',2,0,60000,1000000),row('SUBJECT_END',2,0,60000,900000000)),host,subjects),
}
for name,mutate in [('clock_drift',lambda h:h['rows'][5].update(monotonic_ns=62000000000)),
 ('marker_wrong_tick',lambda h:h['rows'][4].update(tick=40001)),
 ('missing_marker',lambda h:h['rows'].pop()),
 ('reader_error',lambda h:h.update(error='truncated'))]:
 h=copy.deepcopy(host);mutate(h);variants[name]=(log,h,subjects)
rejected=[]
for name,args in variants.items():
 try:costs(*args)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError(name)
parsed=dict(phase_ends=[[1,3,128]],phase_rows=[[1,32,3]],calls={i:dict(api=11,phase=0 if i<=32 else 1) for i in range(1,65)})
extra=[('COST_PID',[12,20,0]),('COST_CREATED',[40,50,0])]
for phase,first,count in [(0,1000,35),(1,40100,160)]:
 step=10 if not phase else 125
 extra.extend([('COST_HIT_START',[phase,first,count]),('COST_HIT_END',[phase,first+(count-1)*step,count])])
 for j in range(count):extra.append(('COST_HIT',[phase,j,first+j*step]))
 for j in range(32):
  ident=1+j+phase*32;tick=first+j*step
  extra.extend([('COST_CALL',[ident,phase,tick]),('COST_RETURN',[ident,phase,tick+1])])
args=(parsed,extra,[12,20,30,40,50],40000,60000,[40000,40000,40100],195)
assert alignment(*args)['strict_interior_hits']==160
variants2=[]
for name,kind,mut in [
 ('missing_entry','COST_HIT',lambda v:[v[0],v[1]+1,v[2]]),
 ('wrong_entry_tick','COST_HIT',lambda v:[v[0],v[1],90000]),
 ('wrong_hit_count','COST_HIT_START',lambda v:[v[0],v[1],v[2]-1]),
 ('late_return','COST_RETURN',lambda v:[v[0],v[1],60001]),
 ('wrong_subject','COST_PID',lambda v:[13,v[1],v[2]]),
 ('wrong_creation','COST_CREATED',lambda v:[41,v[1],v[2]])]:
 e=copy.deepcopy(extra)
 index=next(i for i,(k,v) in enumerate(e) if k==kind and (kind in ['COST_PID','COST_CREATED'] or (v[0]==1 if kind.startswith('COST_HIT') else v[1]==1)))
 e[index]=(kind,mut(e[index][1]));variants2.append((name,(parsed,e,*args[2:])))
variants2.extend([
 ('request_before_start',(parsed,extra,*args[2:5],[39999,40000,40100],195)),
 ('ack_after_end',(parsed,extra,*args[2:5],[40000,40000,60001],195)),
 ('wrong_copy_total',(*args[:-1],194)),
 ('missing_sample_stamp',(parsed,extra[:-1],*args[2:]))])
for name,a in variants2:
 try:alignment(*a)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,sanitized_shared_timing_control=True,
 sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h']},
 scope='Host rejection gates only; actual original continuous NT5 run required.'),indent=2)+'\n')
print('617 host controls passed',len(rejected),'rejections')
