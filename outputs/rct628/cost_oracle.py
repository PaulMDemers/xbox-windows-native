"""Bounded saved-user-location interpretation, separate from kernel CPU attribution."""
from collections import Counter

def analyze(log,host):
 assert host['closed'] and host['connected'] and not host.get('error')
 h=host['rows'];assert [(v['kind'],v['case']) for v in h]==[('START',0),('END',0),('START',5),('END',5)]
 rows={};modules=[];samples=[];done=0
 for line in log.splitlines():
  v=line.split();tag=v[0]
  if tag in ('CODE','STACK','CALLSITE','TARGET'):continue
  if tag=='FREQ':assert len(v)==2 and int(v[1],16)>0;continue
  if tag=='SLEEP_DONE':assert len(v)==1;continue
  if tag=='PROFILE_DONE':done+=1;continue
  assert tag in ['MODULE','SAMPLE','IDENTITY','THREAD_READY','THREAD_START','THREAD_END','SLEEP_START','SLEEP_END','SUBJECT_START','SUBJECT_END','OBSERVER_START','OBSERVER_END']
  case=int(v[1]);assert case==(0 if tag.startswith('SLEEP_') else 4)
  if tag=='MODULE':
   assert len(v)>=5;modules.append((int(v[2],16),int(v[3],16),' '.join(v[4:])));continue
  if tag=='SAMPLE':
   assert len(v)==11;samples.append([int(v[2]),int(v[3]),*[int(x,16) for x in v[4:8]],*[int(x) for x in v[8:]]]);continue
  assert tag not in rows;rows[tag]=v[2:]
 assert done==1 and set(rows)=={'IDENTITY','THREAD_READY','THREAD_START','THREAD_END','SLEEP_START','SLEEP_END','SUBJECT_START','SUBJECT_END','OBSERVER_START','OBSERVER_END'}
 for tag in ['SLEEP_START','SLEEP_END','SUBJECT_START','SUBJECT_END','OBSERVER_START','OBSERVER_END']:assert len(rows[tag])==8
 for tag,marker in [('SLEEP_START',0),('SLEEP_END',1),('SUBJECT_START',2),('SUBJECT_END',3)]:assert int(rows[tag][2])==h[marker]['tick']
 elapsed=(int(rows['SUBJECT_END'][2])-int(rows['SUBJECT_START'][2]))/1000
 host_elapsed=(h[3]['monotonic_ns']-h[2]['monotonic_ns'])/1e9
 assert 20<=elapsed<=21 and abs(elapsed-host_elapsed)<.25
 sleep=(int(rows['SLEEP_END'][2])-int(rows['SLEEP_START'][2]))/1000
 sleep_host=(h[1]['monotonic_ns']-h[0]['monotonic_ns'])/1e9
 assert 4.9<=sleep<=5.2 and abs(sleep-sleep_host)<.25
 def cpu(a,b):
  deltas=[int(b[i],16)-int(a[i],16) for i in [3,4]];assert min(deltas)>=0
  return dict(kernel_seconds=deltas[0]/1e7,user_seconds=deltas[1]/1e7,cpu_seconds=sum(deltas)/1e7)
 game=cpu(rows['SUBJECT_START'],rows['SUBJECT_END']);observer=cpu(rows['OBSERVER_START'],rows['OBSERVER_END'])
 assert game['cpu_seconds']<=elapsed+.1 and observer['cpu_seconds']/elapsed<.15
 a,b=rows['THREAD_START'],rows['THREAD_END'];ready=rows['THREAD_READY']
 assert len(a)==len(b)==3 and len(ready)==4 and a[0]==b[0]==ready[0]
 d=[int(b[i],16)-int(a[i],16) for i in [1,2]];assert min(d)>=0;tcpu=sum(d)/1e7
 assert 0<=tcpu<=game['cpu_seconds']+.015625 and game['cpu_seconds']-tcpu<=.1
 ident=rows['IDENTITY'];assert len(ident)==4
 pid,tid,observerid=map(int,ident[:3]);creation=int(ident[3],16)
 assert pid>0 and tid>0 and observerid>0 and pid!=observerid and creation>0
 assert 1<=len(modules)<=128
 for i,(base,size,name) in enumerate(modules):
  assert base>0 and size>0 and base+size<=2**32
  assert all(base>=b+s or b>=base+size for b,s,_ in modules[:i])
 assert modules[0][2].lower()=='c:\\xwn628-kit\\game\\rct.exe'
 start,end=int(rows['SUBJECT_START'][2]),int(rows['SUBJECT_END'][2]);last=start-1
 assert 100<=len(samples)<=512 and len(samples)==int(rows['SUBJECT_END'][0])
 counts=Counter();sites=Counter()
 for i,(index,tick,eip,esp,ebp,cs,hold,prior,resumed) in enumerate(samples):
  assert index==i and start<=tick<end and tick>last and esp>0 and cs&3==3 and 0<=hold<=100 and prior==0 and resumed==1
  owner=[(b,n) for b,s,n in modules if b<=eip<b+s];assert len(owner)==1
  base,name=owner[0];name=name.lower().split('\\')[-1];counts[name]+=1;sites[name,eip-base]+=1;last=tick
 return dict(passed=True,elapsed_seconds=elapsed,host_seconds=host_elapsed,sleep_seconds=sleep,sleep_host_seconds=sleep_host,
  game=game,observer=observer,main_thread_cpu_seconds=tcpu,identity=[pid,tid,observerid,creation],samples=len(samples),
  module_locations=dict(counts),sites=[dict(module=m,offset=hex(off),samples=n) for (m,off),n in sites.most_common()],
  largest_hold_ms=max(v[6] for v in samples),scope='Saved user instruction locations, not kernel stacks or CPU-time percentages. ntdll locations can occur in busy controls too.')
