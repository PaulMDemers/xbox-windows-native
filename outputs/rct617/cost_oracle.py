"""Qualify uninterrupted work and phase reset after the measurement start."""
from counter_oracle import costs
from trace_oracle import parse

def alignment(parsed,extra,identity,start,end,window,copies=None):
 assert [v for k,v in extra if k=='COST_PID']==[[identity[0],identity[1],0]]
 assert [v for k,v in extra if k=='COST_CREATED']==[[identity[3],identity[4],0]]
 before,after,ack=window
 assert start<=before<=after<=ack<=start+10000 and ack<end
 hits={0:[],1:[]};bounds={};stamps={}
 for kind,v in extra:
  if kind=='COST_HIT':
   phase,index,tick=v;assert phase in hits and index==len(hits[phase]) and index<4096
   if hits[phase]:assert hits[phase][-1]<=tick
   hits[phase].append(tick)
  elif kind in ['COST_HIT_START','COST_HIT_END']:
   phase,tick,count=v;assert phase in hits and (kind,phase) not in bounds
   bounds[kind,phase]=(tick,count)
  elif kind in ['COST_CALL','COST_RETURN']:
   ident,phase,tick=v;key=(kind,ident);assert key not in stamps
   c=parsed['calls'][ident];assert c['api']==11 and c['phase']==phase
   stamps[key]=tick
  else:assert kind in ['COST_PID','COST_CREATED']
 assert len(bounds)==4 and len(stamps)==128
 for phase in [0,1]:
  assert len(hits[phase])>=32
  assert bounds['COST_HIT_START',phase]==(hits[phase][0],len(hits[phase]))
  assert bounds['COST_HIT_END',phase]==(hits[phase][-1],len(hits[phase]))
 assert parsed['phase_rows']==[[1,32,len(hits[0])-32]]
 assert parsed['phase_ends']==[[1,len(hits[0])-32,len(hits[1])-32]]
 assert hits[1][0]>=before and hits[0][-1]<=hits[1][0]
 if copies is not None:assert sum(map(len,hits.values()))==copies
 calls={i:c for i,c in parsed['calls'].items() if c['api']==11}
 assert len(calls)==64 and sum(c['phase']==1 for c in calls.values())==32
 for i,c in calls.items():
  a,b=stamps['COST_CALL',i],stamps['COST_RETURN',i]
  assert a<=b and a in hits[c['phase']]
  if c['phase']:assert before<=a<=b<end
 # Tick endpoints are inclusive ambiguity bands, not sub-tick timestamps.
 inside=[t for values in hits.values() for t in values if start<t<end]
 edge=[t for values in hits.values() for t in values if t in [start,end]]
 assert len(inside)>=32
 return dict(passed=True,hits_per_phase=[len(hits[0]),len(hits[1])],
  strict_interior_hits=len(inside),boundary_tick_hits=len(edge),
  recorded_phase1_pairs=32,request_before_tick=before,request_after_tick=after,
  ack_first_observed_tick=ack,first_phase1_hit=hits[1][0],last_phase1_hit=hits[1][-1],
  scope='All API11 entry timestamps; endpoint-tick hits separate. Counts are not frames.')

def analyze(log,host,subjects,trace):
 windows={};base=[]
 for line in log.splitlines():
  if line.startswith('WINDOW '):
   case,*v=map(int,line.split()[1:]);assert case in [1,2] and case not in windows and len(v)==3
   windows[case]=v
  else:base.append(line)
 assert windows[1]==[0,0,0] and len(windows)==2
 result,rows,identities,subject_times=costs('\n'.join(base),host,subjects)
 extra=[];base=[]
 for line in trace.splitlines():
  if line.startswith('COST_'):
   p=line.split();assert len(p)==4;extra.append((p[0],[int(x,16) for x in p[1:]]))
  else:base.append(line)
 parsed=parse('\n'.join(base))
 for i,c in parsed['calls'].items():
  if c['api']==11:assert c['result']==8 and parsed['args'][i][1:9]==[0,0,8,8,0,0,8,8]
 t=alignment(parsed,extra,identities[2],rows[2,'SUBJECT_START'][0]['tick'],
  rows[2,'SUBJECT_END'][0]['tick'],windows[2],int(subjects[1].split()[9]))
 return dict(passed=True,cases=result,timing=t,trace_pairs=len(parsed['calls']),
  scope='Original continuously running workload; no RCT cost, FPS or acceleration conclusion.')
