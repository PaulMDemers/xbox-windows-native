"""Read-only review of closed282 post-unit graph; never authorizes live disposal."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;parent=k.parent/'release-pair282';sys.path.insert(0,str(parent))
import proof,decode,graph_base,graph_extra
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(g,ui,allocations):
 decode.validate_graph(g,2,allocations,True)
 graph_base.inspect([r for r in g if r[0]<50],[r for r in ui if r[0]<50])
 extra=graph_extra.inspect(g,ui);assert extra['unknown_actor_work']==0
 integers={r[2]:r[3] for r in ui if r[0]==31 and r[1]==3}
 for kind,names in [(54,{integers[0x8ca6],integers[0x8caa]}),(57,{integers[0x85b5]}),(61,{integers[0x8b8d]})]:
  headers=[r for r in ui if r[0]==kind];assert len(headers)==len(names) and {r[2] for r in headers}==names
 selected=[];bindings={r[1]:r for r in g if r[0]==4};accounts={r[1]:r for r in g if r[0]==5};units={r[1]:r for r in g if r[0]==3}
 for t in sorted((r for r in g if r[0]==67),key=lambda r:r[1]):
  unit,identity,name=t[1:4];b=bindings[identity];a=accounts[identity]
  assert units[unit][2:5]==[0,0,1] and b[2:5]==[1,name,0x0de1] and a[2:5]==[1,1,0]
  cache=[r for r in g if r[0]==2 and r[2]==identity];assert len(cache)==1 and cache[0][7]==0
  assert not any(r[0]==32 and r[4]==name for r in g+ui)
  assert not any(r[0]==55 and r[4]==0x1702 and r[5]==name for r in g+ui)
  assert not any(r[0]==40 and name in r[3:6] for r in ui)
  assert not any(r[0]==64 and r[3]==name for r in ui)
  selected.append(dict(unit=unit,identity=identity,gl_name=name,cache_node=cache[0][1],refs=1,unit_edges=0,cache_edges=1,source=t[6],source_bytes=t[7]))
 return dict(selected=selected,contexts=extra['native_contexts'],ui_context=extra['ui_context'],
  total_cache_edges=sum(r[0]==2 for r in g),known_reference_scope_passed=True,live_authorization=False,
  scope='Closed282 known GL4.0/renderer/UI containers, not unknown extensions or current live state')
if __name__=='__main__':
 dest=k/'actual-edges.json';assert not dest.exists();out=parent/'candidate001';t=json.loads((out/'trace.json').read_text())
 assert json.loads((out/'final-review.json').read_text())['closed']
 g=proof.load_pages(out,t,'stage2',2,180000);ui=proof.load_pages(out,t,'ui',1,8192);alloc=t['checkpoints'][0]['state_header'][10:14]
 result=inspect(g,ui,alloc);rejected=0
 def reject(a,b):
  global rejected
  try:inspect(a,b,alloc)
  except (AssertionError,KeyError,IndexError):rejected+=1
  else:raise AssertionError('Invalid closed-graph disposal eligibility accepted')
 for item in result['selected']:
  name=item['gl_name'];identity=item['identity']
  for group in [g,ui]:
   for i,r in enumerate(group):
    if r[0]==32 and r[2]==0:
     m=group.copy();m[i]=r.copy();m[i][4]=name;reject(m,ui) if group is g else reject(g,m)
    if r[0]==55:
     m=group.copy();m[i]=r.copy();m[i][4:6]=[0x1702,name];reject(m,ui) if group is g else reject(g,m)
  for kind,col in [(2,7),(3,2),(3,3),(3,4),(4,2),(5,3),(5,4)]:
   i=next(i for i,r in enumerate(g) if r[0]==kind and (r[1]==item['unit'] if kind==3 else r[2]==identity if kind==2 else r[1]==identity))
   m=g.copy();m[i]=g[i].copy();m[i][col]^=1;reject(m,ui)
  for i,r in enumerate(ui):
   for col in ([3,4,5] if r[0]==40 else [3] if r[0]==64 else []):
    m=ui.copy();m[i]=r.copy();m[i][col]=name;reject(g,m)
 for group in [g,ui]:
  for kind in [30,32,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,67,68,71,72]:
   indices=[i for i,r in enumerate(group) if r[0]==kind]
   if indices:
    i=indices[0];m=group[:i]+group[i+1:];reject(m,ui) if group is g else reject(g,m)
 result.update(actual_mutations_rejected=rejected,source_trace_sha256=sha(out/'trace.json'),script_sha256=sha(Path(__file__)),historical_qualification_changed=False)
 dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
