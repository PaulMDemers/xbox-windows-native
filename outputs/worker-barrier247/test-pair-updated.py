"""Exercise actual counted parser and host intervention with finite adapters."""
import ast,copy,hashlib,json,re,time
from pathlib import Path
from schema import parse,qualify
from preservation import preconditions,preserve_tuple
k=Path(__file__).resolve().parent;dest=k/'pair-test002.json';assert not dest.exists()
old=json.loads((k.parent/'gpu-preserve-empty241/preserve001/trace.json').read_text(encoding='utf-8'))
pre=old['phase_snapshot']['tuple'];pres=old['preservation']['terminal_reply']
stats=[0]*48;stats[0]=1;stats[3]=pre['current_pg_only'][5];stats[14]=512;stats[16]=stats[18]=stats[20]=51200;stats[37]=512;stats[42]=stats[44]=stats[47]=51200
def base():
 slots=[]
 for j in range(2):
  surface=copy.deepcopy(pre['surfaces'])
  if j:
   for v in surface:v[5]&=~3
  slots.append(dict(valid=True,when=102+j,fifo_when=101 if not j else 104,fifo=[1]+pre['current_fifo'][1:],context=pre['context'],stats=stats,surfaces=surface,textures=[],bindings=[[0]*4 for _ in range(4)]))
 return dict(version=242,state=3,published=1,slots=slots)
def report(v):
 d=dict(version=242,state=v['state'],published=v['published'],cpu_callbacks_observed=0,gl_bindings_observed=0,retired=0,native_grant=0)
 if v['published']:
  for j,s in enumerate(v['slots']):
   d[f'slot{j}_valid']=int(s['valid'])
   if not s['valid']:continue
   for key in ['when','fifo_when']:d[f'slot{j}_{key}']=s[key]
   d[f'slot{j}_surfaces']=len(s['surfaces']);d[f'slot{j}_textures']=len(s['textures'])
   for p,key in [('f','fifo'),('c','context'),('r','stats')]:
    for i,x in enumerate(s[key]):d[f'{p}{j}_{i}']=x
   for p,key in [('s','surfaces'),('t','textures'),('b','bindings')]:
    for i,row in enumerate(s[key]):
     for x,value in enumerate(row):d[f'{p}{j}_{i}_{x}']=value
 return ' '.join(f'{key}={value}' for key,value in d.items())
checks=0
def expect(fn,ok):
 global checks
 try:fn();actual=True
 except (AssertionError,KeyError,ValueError):actual=False
 assert actual==ok;checks+=1
expect(lambda:qualify(parse(report(base())),pre),True)
text=report(base())
for t in [text+' state=3',text+' extra=0',text.replace(' b1_3_3=0',''),text.replace('version=242','version=241'),text.replace('cpu_callbacks_observed=0','cpu_callbacks_observed=1'),text.replace('retired=0','retired=1'),text.replace('native_grant=0','native_grant=1'),text.replace('state=3','state=5')]:expect(lambda:parse(t),False)
for field,slot,index,value in [('fifo',0,0,0),('stats',1,0,0),('stats',1,1,2),('stats',1,3,0),('stats',1,13,1),('context',1,0,1),('stats',0,37,513),('stats',0,42,51201)]:
 v=base();v['slots'][slot][field]=copy.deepcopy(v['slots'][slot][field]);v['slots'][slot][field][index]=value;expect(lambda:qualify(parse(report(v)),pre),False)
for key,value in [('when',0),('fifo_when',200)]:
 v=base();v['slots'][0][key]=value;expect(lambda:qualify(parse(report(v)),pre),False)
for col,value in [(0,1),(5,1),(6,0),(9,1)]:
 v=base();v['slots'][1]['surfaces'][0][col]=value;expect(lambda:qualify(parse(report(v)),pre),False)
for state in [0,1,2,5,7]:
 v=dict(state=state,published=0,slots=[]);expect(lambda:parse(report(v)),True);expect(lambda:qualify(parse(report(v)),pre),False)
v=base();v['slots'][1]['valid']=False;expect(lambda:qualify(parse(report(v)),pre),False)
source=k/'trace.py';tree=ast.parse(source.read_text(encoding='utf-8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='preservation_experiment')
for state in [3,4,5,6]:
 calls=[];count=0
 def cmd(s):
  calls.append(s)
  if s.endswith('xwn-inventory242-report'):return report(base())
  if s.startswith('qom-set '):return '(qemu) '
  if not any(v.startswith('qom-set ') for v in calls):return 'state=0'
  result=re.sub(r'(?<![a-z_])state=3','state='+str(state),pres)
  if state==5:
   result=result.replace('tuple_published=1','tuple_published=0')
   for key in ['surfaces','dirty','downloaded','bytes','error','reason','consume_stop','consume_steps','consume_words','wait_before','wait_after']:result=re.sub(r'(?<![a-z_])'+key+r'=\d+',key+'=0',result)
  return result
 ns=dict(r=dict(phase_snapshot=dict(tuple=copy.deepcopy(pre)),nv2a_qom_path='/nv2a'),quarantined=False,preconditions=preconditions,preserve_tuple=preserve_tuple,inventory_tuple=parse,inventory_qualify=qualify,cmd=cmd,case='preserve001',utc=lambda:'adapter',save=lambda:None,out=k/'preserve001',ws=k.parents[1],json=json,re=re,time=time,sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest())
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
 expect(ns['preservation_experiment'],state==3)
 assert sum(s.startswith('qom-set ') for s in calls)==1;checks+=1
 assert not any(s.startswith('pmemsave ') for s in calls);checks+=1
 assert sum(s.endswith('xwn-inventory242-report') for s in calls)==(2 if state==3 else 0);checks+=1
 assert ns['quarantined']==(state in [5,6]);checks+=1
dest.write_text(json.dumps(dict(passed=True,checks=checks,actual_trace_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),schema_sha256=hashlib.sha256((k/'schema.py').read_bytes()).hexdigest(),scope='Actual host parser/intervention with finite adapters; no GPU execution/timing proof',guest_launch=False,physical_access=False),indent=2)+'\n',encoding='utf-8')
print('242 actual parser/intervention adapters PASS',checks)
