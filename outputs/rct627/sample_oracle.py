"""Instruction snapshots are locations, not automatically CPU-time fractions."""
from collections import Counter

def validate_case(case):
 ident=case['identity'];assert len(ident)==4
 pid,tid,observer,created=ident
 assert pid>0 and tid>0 and observer>0 and pid!=observer and created>0
 start,end=case['ticks'];assert 20000<=end-start<=21000
 host=case['host_seconds'];assert abs((end-start)/1000-host)<=.25
 cpu=case['cpu'];thread=case['thread_cpu'];watch=case['observer_cpu'];seconds=(end-start)/1000
 assert 0<=thread<=cpu+.015625 and 0<=cpu<=seconds+.1 and 0<=watch<=seconds+.1
 assert cpu-thread<=.1,'Main-thread coverage missing'
 modules=case['modules'];assert 1<=len(modules)<=128
 for i,(base,size,name) in enumerate(modules):
  assert base>0 and size>0 and base+size<=2**32 and name
  assert all(base>=b+s or b>=base+size for b,s,_ in modules[:i])
 mode=case['mode'];assert mode in range(4)
 assert case['loops']>0 and case['subject_pass'] and case['exit_code']==0
 samples=case['samples'];counts=Counter();known=0;last=start-1
 if case['observed']:assert 100<=len(samples)<=512
 else:assert not samples
 for row in samples:
  index,tick,eip,esp,ebp,cs,hold,prior,resumed=row
  assert index==sum(counts.values()) and start<=tick<end and tick>last
  assert esp>0 and cs&3==3 and 0<=hold<=100 and prior==0 and resumed==1
  owners=[name for base,size,name in modules if base<=eip<base+size];assert len(owners)==1
  counts[owners[0].lower().split('\\')[-1]]+=1;last=tick
 calls=case['loops'];changes=case['changes'];first,lasttimer=case['timer_values'];ss,se=case['subject_ticks']
 assert 0<changes<=calls<2**32 and ss<=start<end<=se and 20000<=se-ss<=22000
 assert 0<=start-ss<=1000 and 0<=se-end<=1000
 assert 19000<=lasttimer-first<=22000 and abs((lasttimer-first)-(se-ss))<=100
 if mode&1:
  assert cpu/seconds<.1 and 100<=calls<=3000
 else:
  assert cpu/seconds>.7 and calls>=100000 and calls%4096==0
 if case['observed']:assert watch/seconds<.15
 return dict(cpu_seconds=cpu,thread_cpu_seconds=thread,observer_cpu_seconds=watch,
  elapsed_seconds=seconds,host_seconds=host,samples=len(samples),modules=dict(counts),
  calls_full_subject_window=calls,subject_window_seconds=(se-ss)/1000,timer_changes=changes,largest_hold_ms=max((v[6] for v in samples),default=0),
  scope='Saved user instruction locations. Not kernel stack samples, FPS or inferred CPU-time percentages.')
