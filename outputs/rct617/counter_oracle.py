def span(a,b):
 assert b['q']>=a['q'] and b['k']>=a['k'] and b['u']>=a['u']
 seconds=(b['tick']-a['tick'])/1000
 cpu=(b['k']-a['k']+b['u']-a['u'])/1e7
 assert 0<seconds<=30 and 0<=cpu<=seconds+.1
 return dict(seconds=seconds,cpu_seconds=cpu)

def costs(log,host,subjects):
 rows={};identities={};cases={};freq=None
 lines=log.splitlines();assert lines[-2:]==['CONTROL_PASS','RESTART']
 for line in lines[:-2]:
  p=line.split();tag=p[0]
  if tag=='FREQ':assert freq is None;freq=int(p[1],16);assert freq>0
  elif tag=='IDENTITY':
   case,*v=map(int,p[1:]);assert case in [1,2] and case not in identities and len(v)==5
   identities[case]=v
  elif tag=='CASE':
   case,n,a,b=map(int,p[1:]);assert case in [1,2] and case not in cases and a==b==0
   cases[case]=n
  else:
   assert tag in ['SLEEP_START','SLEEP_END','SUBJECT_START','SUBJECT_END','TRACER_START',
    'TRACER_END','OBSERVER_START','OBSERVER_END','SUBJECT_SAMPLE','TRACER_SAMPLE'] and len(p)==10
   case,index=int(p[1]),int(p[2]);key=(case,tag);values=rows.setdefault(key,[])
   assert index==len(values) and (tag.endswith('SAMPLE') or not values)
   v=dict(q=int(p[3],16),tick=int(p[4]),k=int(p[5],16),u=int(p[6],16),
     ws=int(p[7]),peak=int(p[8]),page=int(p[9]))
   assert 0<=v['tick']<2**32 and 0<v['ws']<=v['peak']<2**32 and 0<v['page']<2**32
   values.append(v)
 assert set(cases)==set(identities)=={1,2}
 assert host['connected'] and host['closed'] and not host.get('error')
 assert host['clock']=='time.monotonic_ns' and len(host['rows'])==6
 result={};expected={(0,'SLEEP_START'),(0,'SLEEP_END')};subject_times={}
 for case in [0,1,2]:
  prefix='SLEEP' if case==0 else 'SUBJECT'
  a,b=[rows[case,prefix+'_'+suffix][0] for suffix in ['START','END']]
  value=span(a,b)
  h0,h1=host['rows'][2*case:2*case+2]
  for h,kind,v in [(h0,'START',a),(h1,'END',b)]:
   assert (h['case'],h['kind'],h['tick'])==(case,kind,v['tick'])
  hs=(h1['monotonic_ns']-h0['monotonic_ns'])/1e9;assert hs>0
  assert abs(hs-value['seconds'])<=max(.1,.05*hs)
  if case:assert h0['monotonic_ns']>host['rows'][case*2-1]['monotonic_ns']
  value.update(host_seconds=hs,qpc_seconds_diagnostic=(b['q']-a['q'])/freq)
  if not case:
   assert 4.9<=value['seconds']<=8 and value['cpu_seconds']<.25*value['seconds']
  else:
   assert 20<=value['seconds']<=21 and 100<=cases[case]<=512
   sid,rid,oid,cl,ch=identities[case]
   assert sid>0 and oid>0 and sid!=oid and (rid==0 if case==1 else rid>0 and rid not in [sid,oid])
   p=subjects[case-1].split()
   assert p[::2]==['SUBJECT','PID','START','END','COPIES','PASS'] and len(p)==12
   which,pid,begin,finish,copies,passed=map(int,p[1::2])
   assert (which,pid,passed)==(case-1,sid,1) and 175<=copies<512
   assert begin<=a['tick']<b['tick']<=finish and 20000<=finish-begin<=25000
   subject_times[case]=(begin,finish)
   roles={}
   for role in ['SUBJECT','OBSERVER']+(['TRACER'] if case==2 else []):
    x,y=[rows[case,role+'_'+suffix][0] for suffix in ['START','END']]
    expected.update((case,role+'_'+suffix) for suffix in ['START','END'])
    roles[role]=span(x,y)
    assert x['tick']<=a['tick']<=b['tick']<=y['tick'] and y['tick']-x['tick']<=b['tick']-a['tick']+100
    if role!='OBSERVER':
     samples=rows[case,role+'_SAMPLE'];expected.add((case,role+'_SAMPLE'))
     assert len(samples)==cases[case]
     prev=x
     for v in samples:
      assert span(prev,v)['seconds']<=.5 and v['tick']<=y['tick']
      assert v['k']<=y['k'] and v['u']<=y['u'];prev=v
     assert 0<=y['tick']-prev['tick']<=500
     roles[role]['working_set_range']=[min(v['ws'] for v in samples),max(v['ws'] for v in samples)]
   assert sum(v['cpu_seconds'] for v in roles.values())<=value['seconds']+.2
   value.update(roles=roles,samples=cases[case],identity=identities[case],
                workload_seconds=(finish-begin)/1000)
  result[str(case)]=value
 assert set(rows)==expected
 return result,rows,identities,subject_times

