"""Finite causal pairing; requests, unlink, free and frontend fence differ."""
import copy,re
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location("sites257",Path(__file__).with_name("analyze-sites.py"))
_sites=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_sites)

CPU=re.compile(r'^xwn_mem_callback244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) addr=(\d+) len=(\d+) stopped=([01])$')
NV=re.compile(r'^nv2a_lifecycle244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) a=(\d+) b=(\d+)$')

def parse(data, ranges):
 assert len(data)<=16*1024**2 and data.endswith(b'\n'), 'Incomplete/oversized raw log'
 groups257=_sites.parse(data) # Validate every complete new group before old causal checks.
 events=[]
 for number,line in enumerate(data.decode('utf-8',errors='strict').splitlines(),1):
  family='cpu' if line.startswith('xwn_mem_callback244 ') else 'nv' if line.startswith('nv2a_lifecycle244 ') else None
  if not family:continue
  m=(CPU if family=='cpu' else NV).fullmatch(line);assert m,('Malformed lifecycle',number,line)
  keys=['phase','when','thread','ref']+(['addr','len','stopped'] if family=='cpu' else ['a','b'])
  row=dict(zip(keys,map(int,m.groups())),family=family,line=number,ordinal=len(events))
  assert row['thread']>0 and len(events)<100000,'Finite trace/actor bound'
  events.append(row)
 assert events, 'No lifecycle coverage'
 current={};callbacks=[];free_wait={};invalid={};flush={};flushes=[];loans={};completed_loans=[];syncs={};sync_returns=[];marks=[]
 for e in events:
  phase=e['phase'];thread=e['thread'];ref=e['ref'];idx=e['ordinal']
  if e['family']=='cpu':
   assert ref and e['len'], 'Null/empty callback'
   if phase==1:
    prior=current.get(ref);assert prior is None or prior.get('unlink'), 'Reuse before unlink'
    row=dict(ref=ref,generation=1 if prior is None else prior['generation']+1,addr=e['addr'],length=e['len'],request=e,insert=None,remove_request=None,unlink=None,free=None,link=None,invalidate=None)
    current[ref]=row;callbacks.append(row)
   elif phase==5:
    assert thread in free_wait,'Free without this CPU thread unlink'
    row=free_wait.pop(thread);assert [ref,e['addr'],e['len']]==[row['ref'],row['addr'],row['length']]
    assert e['when']>=row['unlink']['when'];row['free']=e
   else:
    assert ref in current;row=current[ref]
    assert [e['addr'],e['len']]==[row['addr'],row['length']]
    if phase==2:
     assert not row['insert'] and not row['unlink'];row['insert']=e
    elif phase==3:
     assert not row['remove_request'] and not row['unlink'];row['remove_request']=e
    elif phase==4:
     assert row['insert'] and row['remove_request'] and not row['unlink'] and thread not in free_wait
     assert row['insert']['thread']==thread and e['when']>=row['insert']['when']
     row['unlink']=e;free_wait[thread]=row
    else:raise AssertionError(('Unknown callback phase',phase))
  elif phase==1:
   assert ref in current;row=current[ref];assert not row['link'] and e['b']==row['length']
   row['link']=e
  elif phase==2:
   if ref:
    assert ref in current and thread not in invalid
    row=current[ref];assert row['link'] and not row['invalidate']
    assert [e['a'],e['b']]==[row['link']['a'],row['link']['b']]
    row['invalidate']=dict(begin=e,end=None);invalid[thread]=row
    if thread in flush:flush[thread]['invalidations'].append([ref,row['generation']])
  elif phase==3:
   if ref:
    assert thread in invalid;row=invalid.pop(thread)
    assert ref==row['ref'] and [e['a'],e['b']]==[row['link']['a'],row['link']['b']]
    row['invalidate']['end']=e
  elif phase==4:
   assert thread not in flush;row=dict(begin=e,end=None,invalidations=[]);flush[thread]=row;flushes.append(row)
  elif phase==5:
   assert thread in flush;flush.pop(thread)['end']=e
  elif phase==10:
   assert not loans, 'Overlapping frontend loans'
   loans[thread]=dict(begin=e,returned=None,selected=None,fence=None,release=None,end=None)
  elif phase in [11,12,30,31,32]:
   assert thread in loans;row=loans[thread]
   if phase==11:
    assert not row['returned'];row['returned']=e
   elif phase==30:
    assert row['returned'] and not row['selected']
    assert bool(e['a'])==(row['returned']['ref']==0)
    if not e['a']:assert e['ref']==row['returned']['ref']
    row['selected']=e
   elif phase==31:
    assert row['selected'] and not row['fence']
    assert [e['ref'],e['a']]==[row['selected']['ref'],row['selected']['a']]
    row['fence']=e
   elif phase==12:
    assert row['fence'] and not row['release'];row['release']=e
   elif phase==32:
    assert row['release'] and [e['ref'],e['a']]==[row['selected']['ref'],row['selected']['a']]
    row['end']=e;completed_loans.append(row);del loans[thread]
  elif phase==20:
   assert thread not in syncs;syncs[thread]=e
  elif phase in [21,22]:
   assert thread in syncs;sync_returns.append(dict(begin=syncs.pop(thread),end=e,null_return=phase==21))
  elif phase in [41,42]:
   assert phase==41+len(marks) and len(marks)<2
   if phase==41:
    targets=[]
    for address,length in ranges:
     found=[row for row in callbacks if row['link'] and not row['invalidate'] and [row['link']['a'],row['link']['b']]==[address,length]]
     assert len(found)==1,('Target correspondence not unique',address,length,len(found))
     targets.append(found[0])
   marks.append(dict(event=e,frontend_inflight=copy.deepcopy(list(loans.values())),cpu_free_inflight=copy.deepcopy(list(free_wait.values()))))
  elif 60<=phase<=68:
   assert ref==0
  elif phase in [70,71,73,74,75,76,77,78,80,82,83]:
   pass #247 individually qualified by worker.py, natural flush data distinct
  elif phase==99 or 100<=phase<=106:
   pass # Complete bounded groups already checked; preserved in ordered event stream.
  else:raise AssertionError(('Unknown NV phase',phase))
 assert len(marks)==2,'Missing finite loader markers'
 boundary=marks[1]['event']['ordinal'];targets_result=[]
 for row in targets:
  complete=bool(row['insert'] and row['remove_request'] and row['unlink'] and row['free'] and row['invalidate'] and row['invalidate']['end'])
  before_boundary=complete and max(row['free']['ordinal'],row['invalidate']['end']['ordinal'])<boundary
  targets_result.append(dict(**row,complete_before_freeldr_marker=bool(before_boundary)))
 observed=dict(events=len(events),callbacks=len(callbacks),inserted=sum(bool(v['insert']) for v in callbacks),remove_requests=sum(bool(v['remove_request']) for v in callbacks),unlinked=sum(bool(v['unlink']) for v in callbacks),freed=sum(bool(v['free']) for v in callbacks),cpu_stopped_frees=sum(bool(v['free'] and v['free']['stopped']) for v in callbacks),flushes=len(flushes),complete_flushes=sum(bool(v['end']) for v in flushes),complete_frontend_loans=len(completed_loans),accelerated_loans=sum(not v['selected']['a'] for v in completed_loans),fallback_loans=sum(bool(v['selected']['a']) for v in completed_loans),sync_null_returns=sum(v['null_return'] for v in sync_returns),sync_null_pending=sum(v['null_return'] and bool(v['end']['b']) for v in sync_returns))
 return dict(causal_pairing_passed=True,observed=observed,events=events,callbacks=callbacks,targets=targets_result,marks=marks,flushes=flushes,frontend_loans=completed_loans,partial_frontend_loans=list(loans.values()),partial_sync=list(syncs.values()),sync_returns=sync_returns,target_callback_retirement_observed=bool(targets_result) and all(v['complete_before_freeldr_marker'] for v in targets_result),display_quiescence=False,full_reference_retirement=False,native_gpu_ownership=False,physical_access=False)
