"""Reject contaminated, unpaired, under-covered and incoherent timing evidence."""
import copy,hashlib,json
from pathlib import Path
from timing import isolation,aggregate
k=Path(__file__).resolve().parent;dest=k/'timing-tests.json';assert not dest.exists();count=0
p=dict(passed=True,timing_passed=True,profile_attribution_passed=True,clock=dict(frequency=1000000,cross_checks=[dict(consistent=True)]),cases=[])
for i in range(45):p['cases'].append(dict(index=i,size=(i%15+(i//15)*5)%15,phases=[dict(target=t,quiet=True,timing_passed=True,loops=1000,qpc_ticks=500000,us_per_draw=500,tick_ms=500) for t in ['primary','memory']]))
assert len(aggregate(p))==30;count+=1
def bad(q):
    global count
    try:aggregate(q)
    except AssertionError:count+=1;return
    raise AssertionError('Invalid phase accepted')
for key in ['passed','timing_passed','profile_attribution_passed']:
    q=copy.deepcopy(p);q[key]=False;bad(q)
q=copy.deepcopy(p);q['cases'].pop();bad(q)
for key,value in [('quiet',False),('timing_passed',False),('loops',0),('qpc_ticks',0),('us_per_draw',-1),('target','other')]:
    q=copy.deepcopy(p);q['cases'][0]['phases'][0][key]=value;bad(q)
q=copy.deepcopy(p);q['clock']['cross_checks'][0]['consistent']=False;bad(q)
q=copy.deepcopy(p);q['cases'][0]['phases'][1]['target']='primary';bad(q)
def utc(i):return f'2026-10-08T20:00:{i:02d}+00:00'
ready=dict(passed=True,same_guest_payloads=True,same_parent_and_chain=True,utc=utc(0));rows=[]
for start in [1,11]:
    rows.append([dict(build_held=True,exclusive_xemu_requested=True,finished=True,owner_pid=4,started_utc=utc(start+1),finished_utc=utc(start+7)),dict(instance_mode='exclusive',instance_pid=5,build_conflict=True,xemu_conflict=True,checked_utc=utc(start+2)),dict(instance_mode='exclusive',instance_pid=5,build_conflict=True,xemu_conflict=True,checked_utc=utc(start+6)),dict(launch_requested_utc=utc(start+3),dashboard_return_utc=utc(start+5),dashboard_return=True,offline_observed=True),dict(pid=4,utc=utc(start))])
audit=dict(utc=utc(20));assert isolation(ready,rows,audit);count+=1
def invalid(rr,aa=audit):
    global count
    try:isolation(ready,rr,aa)
    except AssertionError:count+=1;return
    raise AssertionError('Invalid isolation accepted')
for pos,key,value in [(0,'build_held',False),(0,'finished',False),(0,'owner_pid',9),(1,'build_conflict',False),(2,'xemu_conflict',False),(2,'instance_pid',6),(3,'offline_observed',False),(1,'checked_utc',utc(0))]:
    q=copy.deepcopy(rows);q[0][pos][key]=value;invalid(q)
q=copy.deepcopy(rows);q[0][0]['finished_utc']=utc(15);invalid(q)
invalid(rows,dict(utc=utc(10)))
dest.write_text(json.dumps(dict(passed=True,checks=count,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['timing.py','test-timing.py','timing-comparison.py']}),indent=2)+'\n')
print(f'{count} timing/isolation rejection checks passed')
