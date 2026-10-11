"""Strict UI actor close/reopen evidence; never full shared-context ownership."""
import re
from lifecycle246 import parse
def report(text):
 pairs=re.findall(r'\b([a-zA-Z0-9_]+)=(-?\d+)',text);v=dict((k,int(x)) for k,x in pairs)
 assert len(v)==len(pairs) and v['version']==246 and v['state']==2 and v['ready']==1
 keys={'version','state','ready','when','thread','context','loan','bql','error','texture','fallback','live','fence'}|{f'binding{i}' for i in range(7)}
 assert set(v)==keys and v['loan']==v['bql']==v['error']==0 and v['context']>0 and v['thread']>0
 assert v['fallback'] in [0,1] and v['live'] in [0,1] and v['fence'] in [0x911a,0x911c]
 return v
def qualify(data,closed_report,reread,reopened):
 assert closed_report==reread
 r=report(closed_report);q=report(reopened.replace('state=5 ','state=2 ',1));assert q==r and 'state=5 ' in reopened
 p=parse(data,[]);events=p['events'];own=[e for e in events if e['family']=='nv' and 60<=e['phase']<=68]
 phases=[e['phase'] for e in own];assert len(own)==13 and sorted(phases)==sorted([60,66,67]+[65]*7+[61,63,64]),phases
 by={n:[e for e in own if e['phase']==n] for n in set(phases)}
 req,ack,reopen,done=[by[n][0] for n in [60,61,63,64]]
 begin,end=[by[n][0] for n in [66,67]]
 assert [req['a'],req['b']]==[1,0] and [ack['a'],ack['b']]==[2,0] and [reopen['a'],reopen['b']]==[2,4] and [done['a'],done['b']]==[4,5]
 assert all(e['thread']==r['thread'] for e in own if e['phase'] not in [60,63])
 assert begin['a']==r['texture'] and begin['b']==100000000 and end['a']==r['fence'] and end['b']==0
 assert begin['ordinal']<end['ordinal']<ack['ordinal']<done['ordinal']
 bindings=by[65];assert [e['a'] for e in bindings]==list(range(7))
 assert all(end['ordinal']<e['ordinal']<ack['ordinal'] and e['b']==r[f'binding{i}'] for i,e in enumerate(bindings))
 assert done['when']-ack['when']>=200000000
 before=[x for x in p['frontend_loans'] if x['end'] and x['end']['ordinal']<begin['ordinal']]
 assert before,'No prior completed real UI loan'
 assert not any(e['family']=='nv' and e['phase'] in [10,11,12,30,31,32] and ack['ordinal']<e['ordinal']<done['ordinal'] for e in events)
 assert any(e['family']=='nv' and e['phase']==10 and e['ordinal']>done['ordinal'] for e in events),'No resumed UI loan'
 return dict(passed=True,ui_thread=r['thread'],context=r['context'],texture=r['texture'],fallback=r['fallback'],texture_live=r['live'],bindings=[r[f'binding{i}'] for i in range(7)],fence=r['fence'],closed_interval_ns=done['when']-ack['when'],closed_interval_new_loans=0,prior_completed_loans=len(before),ui_reopened=True,shared_contexts_retired=False,native_gpu_ownership=False)
