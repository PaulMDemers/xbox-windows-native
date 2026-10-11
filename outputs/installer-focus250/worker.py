"""Finite worker/context/park qualification; no full reference retirement."""
import re
from lifecycle247 import parse
def report(text):
 pairs=re.findall(r'\b([a-zA-Z0-9_]+)=(-?\d+)',text);r={k:int(v) for k,v in pairs};assert len(r)==len(pairs)
 assert r['version']==247 and r['state']==3 and r['ready']==1
 assert r['reason']==r['dirty']==r['error']==0 and 0<=r['count']<=128
 keys={'version','state','ready','reason','count','dirty','error','when','thread'}|{f'context{i}' for i in range(2)}|{f'fence{i}' for i in range(2)}|{f'binding{i}' for i in range(14)}|{f'surface{i}_{j}' for i in range(r['count']) for j in range(6)}
 assert set(r)==keys and r['thread']>0
 assert r['context0']>0 and r['context1']>0 and r['context0']!=r['context1']
 assert all(r[f'fence{i}'] in [0x911a,0x911c] for i in range(2))
 for i in range(r['count']):assert r[f'surface{i}_4']==0 and r[f'surface{i}_2']>0
 return r
def qualify(data,closed,reread,released):
 r=report(closed);assert closed==reread
 assert 'state=5 ' in released and report(released.replace('state=5 ','state=3 ',1))==r
 p=parse(data,[]);e=p['events'];w=[x for x in e if x['family']=='nv' and 70<=x['phase']<=80]
 want=[70,71,78,80]+[73]*14+[74]*2+[75]*2+[76]*r['count']+[77]*r['count'];assert sorted(x['phase'] for x in w)==sorted(want)
 by={n:[x for x in w if x['phase']==n] for n in set(want)}
 req,claim,park,end=[by[n][0] for n in [70,71,78,80]]
 assert [req['a'],req['b']]==[1,0] and [claim['a'],claim['b']]==[2,0] and [park['a'],park['b']]==[3,0] and [end['a'],end['b']]==[5,0]
 assert claim['ordinal']<park['ordinal']<end['ordinal'] and end['when']-park['when']>=200000000
 assert all(x['thread']==r['thread'] for x in w if x['phase']!=70)
 assert [x['ref'] for x in by[73]]==list(range(14))
 for i,x in enumerate(by[73]):assert x['a']==r[f'binding{i}'] and x['b']==r[f'context{i//7}'] and claim['ordinal']<x['ordinal']<park['ordinal']
 for i in range(2):
  b,a=by[74][i],by[75][i];assert b['ref']==a['ref']==i and b['a']==100000000 and b['b']==0 and a['a']==r[f'fence{i}'] and a['b']==0
  assert by[73][i*7+6]['ordinal']<b['ordinal']<a['ordinal']<park['ordinal']
 for i in range(r['count']):
  a,b=by[76][i],by[77][i]
  assert a['ref']==b['ref']==r[f'surface{i}_0']
  assert [a['a'],a['b'],b['a'],b['b']]==[r[f'surface{i}_{j}'] for j in [1,2,3,4]]
  assert claim['ordinal']<a['ordinal']<b['ordinal']<park['ordinal']
 # No rendering, reference invalidation or UI loans may occur in the parked span.
 assert not any(x['family']=='nv' and x['phase'] in [1,2,3,4,5,10,11,12,20,21,22,30,31,32,76,77,82,83] and park['ordinal']<x['ordinal']<end['ordinal'] for x in e)
 ui_ack=[x for x in e if x['family']=='nv' and x['phase']==61];ui_open=[x for x in e if x['family']=='nv' and x['phase']==64]
 assert len(ui_ack)==len(ui_open)==1 and ui_ack[0]['ordinal']<claim['ordinal'] and end['ordinal']<ui_open[0]['ordinal']
 natural=[];pending={}
 for x in e:
  if x['family']!='nv':continue
  if x['phase']==82:assert x['thread'] not in pending;pending[x['thread']]=x
  if x['phase']==83:
   a=pending.pop(x['thread']);assert a['ref']==x['ref'];natural.append(dict(surface=x['ref'],addr=a['a'],bytes=a['b'],gl_buffer=x['a'],flags=x['b'],before_ordinal=x['ordinal'],thread=x['thread']))
 assert not pending
 return dict(passed=True,worker_thread=r['thread'],contexts=[r[f'context{i}'] for i in range(2)],bindings=[[r[f'binding{i*7+j}'] for j in range(7)] for i in range(2)],fences=[r[f'fence{i}'] for i in range(2)],surfaces=r['count'],flagged_surfaces=r['dirty'],parked_ns=end['when']-park['when'],worker_released=True,natural_disposals=natural,natural_flagged_disposals=sum(bool(x['flags']) for x in natural),latest_dirty_bytes_at_disposal_preserved=False,full_reference_retirement=False,native_gpu_ownership=False)
