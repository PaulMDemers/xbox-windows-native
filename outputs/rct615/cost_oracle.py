"""Independent integer-counter review. QPC is diagnostic, never elapsed truth."""
def parse(log):
 rows={};frequency=None;count=None;done=[]
 for line in log.splitlines():
  p=line.split()
  if p[0]=='FREQ':
   assert frequency is None and len(p)==2
   frequency=int(p[1],16);assert frequency>0
  elif p[0]=='SAMPLES':
   assert count is None and len(p)==2
   count=int(p[1])
  elif p[0] in ['SLEEP_DONE','COST_DONE']:
   assert len(p)==1 and p[0] not in done
   done.append(p[0])
  else:
   assert p[0] in ['SLEEP_START','SLEEP_END','GAME_START','GAME_END',
                    'OBSERVER_START','OBSERVER_END','SAMPLE'] and len(p)==10
   tag=p[0];case,index=int(p[1]),int(p[2])
   assert case==(0 if tag.startswith('SLEEP') else 1)
   assert index==len(rows.setdefault(tag,[])) if tag=='SAMPLE' else index==0 and not rows.setdefault(tag,[])
   v=dict(q=int(p[3],16),tick=int(p[4]),k=int(p[5],16),u=int(p[6],16),
          ws=int(p[7]),peak=int(p[8]),page=int(p[9]))
   assert all(0<=v[n]<2**64 for n in ['q','k','u'])
   assert 0<=v['tick']<2**32
   assert 0<v['ws']<=v['peak']<2**32 and 0<v['page']<2**32
   rows[tag].append(v)
 assert frequency and done==['SLEEP_DONE','COST_DONE']
 assert set(rows)=={'SLEEP_START','SLEEP_END','GAME_START','GAME_END','OBSERVER_START','OBSERVER_END','SAMPLE'}
 assert count==len(rows['SAMPLE']) and 100<=count<=512
 return rows,frequency

def elapsed(a,b):
 assert b['q']>=a['q'] and b['k']>=a['k'] and b['u']>=a['u']
 dt=((b['tick']-a['tick'])&0xffffffff)/1000
 assert 0<dt<=30
 cpu=(b['k']-a['k']+b['u']-a['u'])/10_000_000
 assert cpu<=dt+.1
 return dt,cpu

def analyze(log,host):
 rows,f=parse(log)
 assert host['connected'] and host['closed'] and not host.get('error')
 assert host['clock']=='time.monotonic_ns' and len(host['rows'])==4
 result={}
 for case,label,prefix in [(0,'sleep','SLEEP'),(1,'game','GAME')]:
  a,b=rows[prefix+'_START'][0],rows[prefix+'_END'][0]
  tick,cpu=elapsed(a,b)
  h0,h1=host['rows'][2*case:2*case+2]
  for h,kind,v in [(h0,'START',a),(h1,'END',b)]:
   assert h['kind']==kind and h['case']==case and h['tick']==v['tick']
  ns=h1['monotonic_ns']-h0['monotonic_ns'];assert ns>0
  seconds=ns/1e9
  assert abs(seconds-tick)<=max(.1,.05*seconds)
  assert (4.9<=tick<=8 and cpu<tick*.25) if case==0 else 20<=tick<=21
  result[label]=dict(tick_seconds=tick,host_seconds=seconds,cpu_seconds=cpu,
    cpu_fraction=cpu/tick,qpc_seconds_diagnostic=(b['q']-a['q'])/f,
    working_set_start=a['ws'],working_set_end=b['ws'],
    pagefile_start=a['page'],pagefile_end=b['page'])
 assert host['rows'][2]['monotonic_ns']>host['rows'][1]['monotonic_ns']
 a,b=rows['GAME_START'][0],rows['GAME_END'][0]
 oa,ob=rows['OBSERVER_START'][0],rows['OBSERVER_END'][0]
 ot,oc=elapsed(oa,ob)
 assert oa['tick']<=a['tick']<=b['tick']<=ob['tick'] and ot<=result['game']['tick_seconds']+.1
 previous=a
 for v in rows['SAMPLE']:
  dt,cpu=elapsed(previous,v);assert dt<=.5
  assert v['tick']<=b['tick'] and v['k']<=b['k'] and v['u']<=b['u']
  previous=v
 assert b['q']>=previous['q'] and 0<=b['tick']-previous['tick']<=500
 samples=rows['SAMPLE']
 result.update(passed=True,samples=len(samples),frequency_diagnostic=f,
   observer_cpu_seconds=oc,observer_elapsed_seconds=ot,
   working_set_range=[min(v['ws'] for v in samples),max(v['ws'] for v in samples)],
   pagefile_range=[min(v['page'] for v in samples),max(v['page'] for v in samples)],
   scope='Paused exact scene in single-CPU PC emulator. Coarse process accounting; not game FPS or Xbox performance.')
 return result
