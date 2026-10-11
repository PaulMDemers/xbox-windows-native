"""Independent actual callback lifetime and site evidence; never flags => pixels."""
import importlib.util,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('sites257',Path(__file__).resolve().parent/'analyze-sites.py');sites=importlib.util.module_from_spec(spec);spec.loader.exec_module(sites)
CPU=re.compile(r'^xwn_mem_callback244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) addr=(\d+) len=(\d+) stopped=([01])$')
NV=re.compile(r'^nv2a_lifecycle244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) a=(\d+) b=(\d+)$')
def value(report,key):
 values=re.findall(r'(?<!\w)'+re.escape(key)+r'=(\d+)',report);assert len(values)==1,(key,len(values));return int(values[0])
def events(data):
 assert len(data)<=32*1024**2 and data.endswith(b'\n')
 rows=[]
 for line in data.decode('utf-8').splitlines():
  rx=CPU if line.startswith('xwn_mem_callback244 ') else NV if line.startswith('nv2a_lifecycle244 ') else None
  if rx is None:continue
  m=rx.fullmatch(line);assert m,'Malformed causal line'
  keys=['phase','when','thread','ref']+(['addr','length','stopped'] if rx==CPU else ['a','b'])
  rows.append(dict(zip(keys,map(int,m.groups())),family='cpu' if rx==CPU else 'nv'))
  assert len(rows)<100000
 return rows
def stage(trace,n):
 p=trace['checkpoints'][n-1];assert p['stage']==n and p['attestation']['passed'] and p['state']==5
 rep=p['renderer_report'];key=lambda name:value(rep,f'slot{n}_'+name)
 assert all(key(x)==0 for x in ['reason','result','callback_result','unknown_vertex'])
 for i in [0,1]:assert key(f'cpu{i}_done')==1 and key(f'cpu{i}_reason')==0
 assert key('started')<key('finished')
 return dict(start=key('started'),end=key('finished'),surface=key('surface'),callback=key('callback'),worker=key('worker'),address=p['attestation']['physical']+4096,size=704)
def lifetime(rows,ref,start,end,address,size):
 cpu=[r for r in rows if r['family']=='cpu' and r['ref']==ref and start<=r['when']<=end]
 assert sorted(r['phase'] for r in cpu)==[1,2,3,4,5],'Exactly one real callback lifetime required'
 c={r['phase']:r for r in cpu}
 assert all((r['addr'],r['length'])==(c[1]['addr'],size) for r in cpu)
 assert c[1]['when']<=c[2]['when']<=c[4]['when']<=c[5]['when'] and c[1]['when']<=c[3]['when']<=c[4]['when']
 assert c[2]['thread']==c[4]['thread']==c[5]['thread'] and c[1]['thread']==c[3]['thread']
 nv=[r for r in rows if r['family']=='nv' and r['ref']==ref and r['phase'] in [1,2,3] and start<=r['when']<=end]
 assert sorted(r['phase'] for r in nv)==[1,2,3]
 d={r['phase']:r for r in nv};assert all((r['a'],r['b'])==(address,size) for r in nv)
 assert d[1]['when']<=d[2]['when']<=d[3]['when'] and d[2]['when']<=c[3]['when']
 assert c[1]['when']<=d[1]['when'] and all(r['thread']==c[1]['thread'] for r in nv)
 return dict(callback=ref,physical_address=address,bytes=size,cpu=cpu,renderer=nv,ramblock_offset=c[1]['addr']-address)
def prove(data,trace,full=False):
 rows=events(data);parsed=sites.parse(data);assert not parsed['truncated_sites']
 one=stage(trace,1);life=lifetime(rows,one['callback'],one['start'],one['end'],one['address'],704)
 target=[r for r in parsed['rows'] if r['callback']==one['callback'] and one['start']<=r['when']<=one['end']]
 assert [r['site'] for r in target]==[2,6] and target[0]['flags']&1 and target[1]['flags']==0
 assert all(r['surface']==one['surface'] and r['address']==one['address'] and r['size']==704 and not r['binding_bits'] for r in target)
 assert target[0]['texture']==target[1]['texture'] and target[0]['texture']>0
 result=dict(age_callback_lifetime=life,age_sites=target,age_lifecycle_passed=True,full_callback_lifecycle_passed=False,pixel_preservation_proved=False)
 if full:
  two,three,four=[stage(trace,i) for i in [2,3,4]]
  assert one['end']<two['start']<two['end']<three['start']<three['end']<four['start']<four['end']
  assert two['callback']==three['callback']==four['callback'] and two['surface']==three['surface']==four['surface']
  assert one['address']==two['address']==three['address']==four['address']
  second=lifetime(rows,two['callback'],two['start'],four['end'],two['address'],704)
  target=[r for r in parsed['rows'] if r['callback']==two['callback'] and two['start']<=r['when']<=four['end']]
  reads=[r for r in target if r['site']==11 and two['end']<=r['when']<three['start'] and r['flags']&1]
  writes=[r for r in target if r['site']==12 and three['end']<=r['when']<four['start'] and r['flags']&1]
  evictions=[r for r in target if r['site']==3 and three['end']<=r['when']<four['start']]
  common=[r for r in target if r['site']==6 and three['end']<=r['when']<four['start']]
  assert all(r['flags']==8 for r in evictions+common),'Upload intent only; dirty/download/evict bits must be clear'
  assert reads and writes and len(evictions)==len(common)==1
  assert all(r['surface']==two['surface'] and r['address']==two['address'] and r['size']==704 and not r['binding_bits'] for r in target)
  assert len({r['texture'] for r in target})==1
  result.update(full_callback_lifecycle_passed=True,read_store_lifetime=second,read_store_sites=target)
 return result
