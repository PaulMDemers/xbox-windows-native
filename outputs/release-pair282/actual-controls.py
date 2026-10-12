"""New read-only mutations of closed actual evidence; no recollection/relaunch."""
import copy,hashlib,json,struct
from pathlib import Path
import checks,proof,decode,transport
k=Path(__file__).resolve().parent;dest=k/'actual-controls001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rejected=0;before={}
def reject(fn):
 global rejected
 try:fn()
 except (AssertionError,KeyError,IndexError,struct.error):rejected+=1
 else:raise AssertionError('Invalid actual evidence accepted')
r=dict(passed=False,read_only=True,guests_relaunched=False,originals_changed=False)
try:
 for case in ['control001','candidate001']:
  out=k/case;assert json.loads((out/'final-review.json').read_text())['closed']
  t=json.loads((out/'trace.json').read_text());mode=case.startswith('candidate');root=Path('E:/xwn282')/case
  before[str(out/'trace.json')]=sha(out/'trace.json')
  groups=[proof.load_pages(out,t,f'stage{i}',i,180000) for i in range(1,4)];alloc=t['checkpoints'][0]['state_header'][10:14]
  ui=proof.load_pages(out,t,'ui',1,8192);checks.initial(t['initial_report'],groups[:2],ui,alloc,mode)
  complete=checks.final(t['initial_report'],t['terminal_report'],groups,ui,alloc,mode)
  for stage,g in enumerate(groups,1):
   for kind in [64,69,70,71,72]:
    i=next(i for i,v in enumerate(g) if v[0]==kind)
    reject(lambda i=i:decode.validate_graph(g[:i]+g[i+1:],stage,alloc,mode))
   for kind,col in [(3,2),(4,2),(5,3),(5,4),(67,2),(67,4),(68,4),(68,6)]:
    selected={v[2] for v in g if v[0]==67}
    indices=[i for i,v in enumerate(g) if v[0]==kind and (kind not in (4,5) or v[1] in selected)]
    for i in indices:
     m=g.copy();m[i]=g[i].copy();m[i][col]^=1
     reject(lambda:decode.validate_graph(m,stage,alloc,mode))
   for a in range(4):
    bad=alloc.copy();bad[a]+=4096;reject(lambda:decode.validate_graph(g,stage,bad,mode))
  records=complete['records']
  for i in range(2):
   for j in range(13):
    m=copy.deepcopy(records);m[i][j]^=1;reject(lambda:transport.inspect(m,groups,mode))
  worker=records[0][10];context=int(complete['graphs'][0]['extension']['native_contexts']['1'])
  for u in range(4):
   for stage in [0,2,1]:
    p=root/f'watch/unit-{u}-stage-{stage}.bin';before[str(p)]=sha(p);data=p.read_bytes();physical=t['checkpoints'][0]['state_header'][18+u]
    proof.snapshot(data,u,stage,physical,worker,context)
    for off in range(len(data)-1024,len(data)):
     m=bytearray(data);m[off]^=1;reject(lambda:proof.snapshot(bytes(m),u,stage,physical,worker,context))
 assert all(sha(Path(p))==h for p,h in before.items())
 r.update(passed=True,mutations_rejected=rejected,original_hashes=before,
          scope='Actual three-boundary scalar/ref/identity/native allocation records and all source/RGBA bytes; mutations are local copies only')
except BaseException as e:r['error']=repr(e)
r['script_sha256']=sha(Path(__file__));dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='original_hashes'},indent=2));assert r['passed']
