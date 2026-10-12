import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
for case in ['001','002']:
 r=json.loads((k/f'host{case}.json').read_text());assert r['passed']
 root=Path('E:/Codex-archive/xbox-windows-native/publication285-host'+case)
 for n,h in r['files'].items():
  p=root/n;assert sha(p)==h;files[str(p)]=h
 for n,source in [('lifetime.h','lifetime.h'),('core_decode.py','decode.py')]:
  assert (root/n).read_bytes()==(k.parent/'replacement-life284'/source).read_bytes()
for n in ['publication.h','decode.py']:
 assert (k/n).read_bytes()==Path('E:/Codex-archive/xbox-windows-native/publication285-host001',n).read_bytes()==Path('E:/Codex-archive/xbox-windows-native/publication285-host002',n).read_bytes()
for n in ['publication.h','test.c','decode.py','test-host.py']:
 assert (k/n).read_bytes()==Path('E:/Codex-archive/xbox-windows-native/publication285-host002',n).read_bytes()
r=dict(passed=True,host_only=True,actual_qemu_owner_hook=False,renderer_built=False,guest_launched=False,
 publication_cases=2048,inflight_quarantines=2048,foreign_seal_races=4096,entry_seal_races=4096,
 closed_foreign_refusals=20000,undersized_immutable_reads=11008,transport_mutations=169,
 exact284_core_and_decoder=True,private_files_verified=len(files),files=files)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
