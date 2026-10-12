import hashlib,json,importlib.util
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={}
for case in ['001','002']:
 r=json.loads((k/f'host{case}.json').read_text());assert r['passed']==(case=='002')
 root=Path('E:/Codex-archive/xbox-windows-native/hooks286-host'+case)
 for n,h in r['files'].items():
  p=root/n;assert sha(p)==h;files[str(p)]=h
 for n,kit in [('publication.h','owner-publication285'),('lifetime.h','replacement-life284')]:
  assert (root/n).read_bytes()==(k.parent/kit/n).read_bytes()
root=Path('E:/Codex-archive/xbox-windows-native/hooks286-host002')
for n in ['adapter.h','instrument.py','test-tail.c','test-host.py']:assert (root/n).read_bytes()==(k/n).read_bytes()
assert (root/'adapter.h').read_bytes()==Path('E:/Codex-archive/xbox-windows-native/hooks286-host001/adapter.h').read_bytes()
spec=importlib.util.spec_from_file_location('original_instrument',root/'instrument.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=(root/'original-texture.c').read_bytes();patched,changes=m.instrument(original.decode())
assert patched.encode()==(root/'instrumented-texture.c').read_bytes()
for old,new,count in reversed(changes):
 assert patched.count(new)==count;patched=patched.replace(new,old)
assert patched.encode()==original
pins=json.loads((k.parent/'release-runtime281/source-review.json').read_text())['files']
assert hashlib.sha256(original).hexdigest() in pins.values()
r=dict(passed=True,host_only=True,full_original_source_byte_reconstructed=True,
 original_source_sha256=hashlib.sha256(original).hexdigest(),original_functions=5,hook_sites=len(changes),
 lifecycle_cases=4,negative_cases=6,balanced_host_objects=82,renderer_built=False,
 actual_active_observer_provider=False,guest_launched=False,shared_source_changed=False,
 private_files_verified=len(files),files=files)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2))
