import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
original=(k.parent/'release-worker280/boundary.h').read_text()
marker='    for(unsigned i=0;i<4;i++) {\n        const X277Texture *t=&p->textures[i];'
assert original.count(marker)==1
prefix=original[:original.index(marker)]
expected=prefix.replace('x280_validate(const X277Proof *p,unsigned candidate)','x287_common(const X277Proof *p)').replace('(candidate>1 || p->stage<1 || p->stage>3)','(p->stage<1 || p->stage>4)')+'    return X277_OK;\n}\n'
for case in ['001','002','003']:
 r=json.loads((k/f'host{case}.json').read_text());assert r['passed']==(case!='002')
 root=Path('E:/Codex-archive/xbox-windows-native/boundary287-host'+case)
 for n,h in r['files'].items():
  p=root/n;assert sha(p)==h;files[str(p)]=h
 assert (root/'common.h').read_bytes()==expected.encode()
 assert (root/'admission.h').read_bytes()==(k.parent/'release-worker280/admission.h').read_bytes()
for n in ['boundary.h','test.c','test-host.py']:
 assert (k/n).read_bytes()==Path('E:/Codex-archive/xbox-windows-native/boundary287-host003',n).read_bytes()
r=dict(passed=True,host_only=True,checks=596,actual_collector=False,actual_provider=False,
 actual_worker=False,renderer_built=False,guest_launched=False,old_validators_unchanged=True,
 common_difference='Only new signature and stage1..4 bound; original CPU/surface prefix otherwise exact',
 preserved_failure='host002 accepted decreasing global mutation clock across guest resume;003 rejects',
 private_files_verified=len(files),files=files)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
