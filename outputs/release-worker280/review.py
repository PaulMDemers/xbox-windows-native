"""Read-only source lineage and complete private host-capsule verification."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=k.parent/'texture-boundary278';proposal=k.parent/'unbound-release279'
assert (k/'admission.h').read_bytes()==(old/'admission.h').read_bytes()
for n in ['release.h','proposed-release.c']:assert (k/n).read_bytes()==(proposal/n).read_bytes()
def function(s,name):
 p=s.index(name+'(');start=s.rfind('static ',0,p);end=s.index('{',p)+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[start:end]
original=function((old/'admission.h').read_text(),'x277_validate')
expected=original.replace('x277_validate(const X277Proof *p)','x280_validate(const X277Proof *p,unsigned candidate)')
expected=expected.replace('(p->stage!=1 && p->stage!=2)','(candidate>1 || p->stage<1 || p->stage>3)')
expected=expected.replace('t->refs!=2','t->refs!=(unsigned)(1+!(candidate && p->stage==2))').replace('t->unit_edges!=1','t->unit_edges!=(unsigned)!(candidate && p->stage==2)')
assert function((k/'boundary.h').read_text(),'x280_validate')==expected
parent=Path('E:/Codex-archive/xbox-windows-native/boundary278-build002/source/hw/xbox/nv2a/pgraph/gl/renderer.c')
pins=json.loads((old/'renderer-source-pins002.json').read_text())
assert sha(parent)==pins['hw/xbox/nv2a/pgraph/gl/renderer.c']
for n in ['x278_cpu_copy','x278_quiescent','x278_publish']:
 assert function(parent.read_text(),n)==function((old/'adapter.c').read_text(),n)
capsules=[];verified=0
for family,ids in [('worker',['001','002','003','004']),('graph',['001']),('publication',['001']),('transport',['001'])]:
 for attempt in ids:
  record=json.loads((k/(family+'-host'+attempt+'.json')).read_text())
  root=Path('E:/Codex-archive/xbox-windows-native/release280-'+family+attempt)
  for n,h in record['files'].items():assert sha(root/n)==h,(family,attempt,n);verified+=1
  assert record['passed']==(family!='worker' or attempt!='001')
  capsules.append(dict(family=family,attempt=attempt,passed=record['passed'],files=len(record['files'])))
for n in ['capture.c','worker.c','validate.c','retained.c','publish.c','scalar-publish.c','boundary.h','link.h','resume.h','transaction.h','test-worker.c']:
 assert (k/n).read_bytes()==(Path('E:/Codex-archive/xbox-windows-native/release280-worker004')/n).read_bytes(),n
assert (k/'graph.c').read_bytes()==Path('E:/Codex-archive/xbox-windows-native/release280-graph001/graph.c').read_bytes()
for n in ['decode.py','transport.py','test-transport.py']:
 assert (k/n).read_bytes()==(Path('E:/Codex-archive/xbox-windows-native/release280-transport001')/n).read_bytes(),n
for n in ['publish.c','transaction.h','test-publication.c']:
 assert (k/n).read_bytes()==(Path('E:/Codex-archive/xbox-windows-native/release280-publication001')/n).read_bytes(),n
compiler=subprocess.check_output(['wsl','-d','Ubuntu','-u','root','--','python3','-c',
 'import hashlib,json,pathlib,shutil,subprocess;p=pathlib.Path(shutil.which("gcc")).resolve();print(json.dumps(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),version=subprocess.check_output([str(p),"--version"],text=True))))'],text=True)
result=dict(passed=True,host_only=True,renderer_built=False,guest_launched=False,physical_access=False,
            original277_and279_byte_identical=True,boundary_delta_only_stage_ref_rules=True,
            original278_functions_exact=True,private_host_files_verified=verified,capsules=capsules,
            gcc=json.loads(compiler),runtime_integrated=False,owned_sessions=[],
            remaining=['actual full graph/UI authorization provider','release and post-snapshot wrappers','QOM request/getter dispatcher and complete runtime transport','matched fresh control and candidate guest qualification'],
            files={p.name:sha(p) for p in k.iterdir() if p.is_file() and p.name!='source-review.json'})
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({a:b for a,b in result.items() if a!='files'},indent=2))
