"""Actual sampler and raw parser with bounded failure adapters; no guest."""
import ast,copy,hashlib,json,re
from pathlib import Path
from parsing import snapshot_tuple
k=Path(__file__).resolve().parent;dest=k/'snapshot-test001.json';assert not dest.exists();checks=0
old=json.loads((k.parent/'guest-gpu-handoff236/trace001/trace.json').read_text());raw=old['wait_irq_snapshot']['reply'].replace('version=234','version=238');extra=' fifo_when=1 renderer_valid=1 surface_count=0 surface_truncated=0 fifo='+','.join(['0']*14)+' context='+','.join(['0']*20);raw+=extra;parsed=snapshot_tuple(raw);assert parsed['wait_labels']==['FIFO access disabled'];checks+=1
fields=parsed['header'];rows=[parsed['current_pg_only']]+parsed['events']
def render(fields,rows):return ' '.join(f'{a}={b}' for a,b in fields.items())+' '+' '.join('row='+','.join(map(str,r)) for r in rows)+extra
assert snapshot_tuple(render(fields,rows))==parsed;checks+=1
mutations=[]
for key,value in [('version',233),('state',5),('tuple_published',0),('capacity',255),('count',257),('total',2**64),('overwritten',0)]:
 f=dict(fields);f[key]=value;mutations.append(render(f,rows))
for index,column,value in [(0,0,1),(0,2,5),(0,10,1),(0,11,123),(1,0,0),(1,1,2**63),(1,3,2**32),(1,9,16),(1,10,2),(1,2,8)]:
 r=copy.deepcopy(rows);r[index][column]=value;mutations.append(render(fields,r))
mutations += [render(fields,rows[:-1]),render(fields,rows)+' state=3',render(fields,[r[:-1] for r in rows])]
for reply in mutations:
 try:snapshot_tuple(reply)
 except AssertionError:checks+=1
 else:raise AssertionError('Malformed tuple accepted')
for mask in range(16):
 r=copy.deepcopy(rows);r[0][9]=mask;v=snapshot_tuple(render(fields,r));assert len(v['wait_labels'])==mask.bit_count();checks+=1
source=k/'trace.py';tree=ast.parse(source.read_text());fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='take_snapshot'];assert len(fn)==1
body=compile(ast.Module(body=fn,type_ignores=[]),str(source),'exec')
class Clock:
 def __init__(self):self.now=0
 def monotonic(self):return self.now
 def sleep(self,s):assert 0<=s<=.025;self.now+=s
for mode in ['published','timeout','changed','refused']:
 calls=[];r={};clock=Clock();reads=0
 def cmd(text):
  global reads
  calls.append(text)
  if text=='info qom-tree':return 'tree'
  if 'qom-set' in text:return 'Error request refused' if mode=='refused' else ''
  reads+=1
  if reads==1:return 'state=0'
  if mode=='timeout':return 'state=5 tuple_published=0'
  if reads==2:return 'state=1'
  if mode=='changed' and reads==4:return raw+' changed'
  return raw
 ns=dict(stopped=True,r=r,phase='xbe',qom_path=lambda t:'/nv2a',cmd=cmd,re=re,save=lambda:None,utc=lambda:'host',time=clock,snapshot_tuple=snapshot_tuple)
 exec(body,ns)
 try:ns['take_snapshot']('actual_xromwell_xbe_entry',[0]*10);success=True
 except AssertionError:success=False
 assert success==(mode=='published') and sum('qom-set' in c for c in calls)==1;checks+=2
 if mode=='timeout':assert r['phase_snapshot']['terminal_state']==5 and 'tuple' not in r['phase_snapshot'];checks+=2
 if mode=='changed':assert not r['phase_snapshot']['immutable_reread_matched'];checks+=1
 try:ns['take_snapshot']('again',[0]*10)
 except AssertionError:checks+=1
 else:raise AssertionError('One-shot repeated')
 assert sum('qom-set' in c for c in calls)==1;checks+=1
record=dict(passed=True,checks=checks,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),parser_sha256=hashlib.sha256((k/'parsing.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),actual_sampler_executed=True,guest_launch=False,physical_access=False)
for suffix in [' renderer_valid=1',' surface=1,2',' fifo_when=2',' context=0']:
 try:snapshot_tuple(raw+suffix)
 except AssertionError:checks+=1
 else:raise AssertionError('Malformed extension accepted')
for key,old,new in [('renderer_valid','1','2'),('surface_count','0','129'),('surface_truncated','0','1'),('fifo_when','1','0')]:
 try:snapshot_tuple(raw.replace(key+'='+old,key+'='+new))
 except AssertionError:checks+=1
 else:raise AssertionError('Invalid reference metadata accepted')
record['checks']=checks
dest.write_text(json.dumps(record,indent=2)+'\n');print('238 snapshot checks',checks)
