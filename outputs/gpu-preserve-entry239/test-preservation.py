"""Actual parsing/preconditions and actual experiment function under bounded adapters."""
import ast,copy,hashlib,json,re,struct,time,datetime
from pathlib import Path
from preservation import preconditions,preserve_tuple
k=Path(__file__).resolve().parent;dest=k/'preservation-test003.json';assert not dest.exists()
old=json.loads((k.parent/'gpu-reference-snapshot238/xbe001/trace.json').read_text(encoding='utf-8'))['phase_snapshot']['tuple']
checks=0
def expect(fn,ok):
 global checks
 try:fn();actual=True
 except (AssertionError,ValueError,KeyError):actual=False
 assert actual==ok;checks+=1
expect(lambda:preconditions(old),True)
for key,value in [('renderer_valid',0),('surface_truncated',1),('current_fifo_valid',False),('wait_mask',2)]:
 t=copy.deepcopy(old);t[key]=value;expect(lambda:preconditions(t),False)
for key,width in [('current_fifo',14),('context',8)]:
 for index in range(width):
  if key=='current_fifo' and index not in [0,2,4,5,6]:continue
  t=copy.deepcopy(old);t[key][index]=1;expect(lambda:preconditions(t),False)
for index,value in [(0,2**32),(1,0),(2,2**32),(3,0),(4,0),(5,0),(5,13),(6,0)]:
 t=copy.deepcopy(old);t['surfaces'][0][index]=value;expect(lambda:preconditions(t),False)
t=copy.deepcopy(old);t['surfaces'][0][0]=t['surfaces'][1][0];expect(lambda:preconditions(t),False)
base=dict(state=3,tuple_published=1,publication_version=232,surfaces=3,dirty=3,downloaded=3,bytes=3072000,error=0,reason=0,references_retired=0,native_grant=0,old_halt=0,consume_stop=0,consume_steps=0,consume_words=0,wait_before=0,wait_after=0)
for label in ['request','gate']:
 for i,v in enumerate(old['current_fifo'][4:14]):base[f'{label}{i}']=v
report=lambda d:' '.join(f'{a}={b}' for a,b in d.items())
expect(lambda:preserve_tuple(report(base)),True)
for key,value in [('state',7),('tuple_published',0),('publication_version',239),('native_grant',1),('references_retired',1),('surfaces',129),('downloaded',4),('bytes',2**64)]:
 d=dict(base);d[key]=value;expect(lambda:preserve_tuple(report(d)),False)
for text in [report(base)+' state=3',report(base).replace(' old_halt=0',''),report(base)+' extra=0']:
 expect(lambda:preserve_tuple(text),False)
for state in [4,5,6]:
 d=dict(base,state=state)
 if state==5:
  d['tuple_published']=0
  for key in ['surfaces','dirty','downloaded','bytes','error','reason','consume_stop','consume_steps','consume_words','wait_before','wait_after']:d[key]=0
 expect(lambda:preserve_tuple(report(d)),True)
# Run the actual new function, including one setter, immutable reread,
# refusal/timeout quarantine and finite RAM capture with no guest connected.
source=k/'trace.py';tree=ast.parse(source.read_text(encoding='utf-8'))
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='preservation_experiment')
root=k/'artifacts/test-preservation003';assert not root.exists();root.mkdir()
for case,state in [('control001',0),('preserve001',3),('preserve001',4),('preserve001',5),('preserve001',6)]:
 out=root/f'{case}-{state}';(out/'artifacts').mkdir(parents=True)
 calls=[];d=dict(base,state=state)
 if state==5:
  d['tuple_published']=0
  for key in ['surfaces','dirty','downloaded','bytes','error','reason','consume_stop','consume_steps','consume_words','wait_before','wait_after']:d[key]=0
 def cmd(text):
  calls.append(text)
  if text.startswith('pmemsave '):
   parts=text.split(' ',3);p=Path(json.loads(parts[3]));p.write_bytes(bytes(int(parts[2])));return '(qemu) '
  if text.startswith('qom-set '):return '(qemu) '
  if sum(c.startswith('qom-set ') for c in calls)==0:return 'state=0 '
  return report(d)
 ns=dict(r=dict(phase_snapshot=dict(tuple=copy.deepcopy(old)),nv2a_qom_path='/nv2a'),quarantined=False,preconditions=preconditions,preserve_tuple=preserve_tuple,cmd=cmd,case=case,utc=lambda:'test',save=lambda:None,out=out,ws=k.parents[1],json=json,re=re,time=time,sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest())
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
 expect(ns['preservation_experiment'],state in [0,3])
 assert sum(c.startswith('qom-set ') for c in calls)==int(case=='preserve001');checks+=1
 assert ns['quarantined']==(state in [5,6]);checks+=1
 assert len([c for c in calls if c.startswith('pmemsave ')])==(3 if state==3 else 0);checks+=1
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=checks,actual_trace_source_sha256=sha(source),parser_sha256=sha(k/'preservation.py'),scope='Actual host functions with finite adapters; not GPU or guest timing proof'),indent=2)+'\n',encoding='utf-8')
print('239 actual preservation adapters PASS',checks)
