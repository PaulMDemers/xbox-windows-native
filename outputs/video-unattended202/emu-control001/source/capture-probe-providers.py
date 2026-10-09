"""Read-only actual probe provider pin, supplement fresh202 capture; no staging or launch."""
import hashlib
import importlib.util
import json
from pathlib import Path
k=Path(__file__).resolve().parent
ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
dest=k/'probe-providers.json'
assert not dest.exists()
capture=read(k/'capture.json');assert capture['passed']
build=read(k.parent/'video-phase-runtime199/build-review.json');assert build['passed']
spec=importlib.util.spec_from_file_location('ftp_helpers',k.parent/'fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=dict(passed=False,physical_access=True,physical_writes=False,launch=False,files=[],all_providers=[])
with m.connect() as f:
    m.owner(f)
    for name,provider in read(k/'build-review.json')['providers'].items():
        path='/F/winnt/system32/'+name.lower()
        row=next((v for v in capture['files'] if v['path'].lower()==path.lower()),None)
        if row:
            assert row['sha256']==provider['sha256'] and row['second_read_exact']
        else:
            data=m.get(f,path);assert sha(data)==provider['sha256']
            p=k/'artifacts'/path.lstrip('/');assert not p.exists()
            p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(data)
            assert m.get(f,path)==data
            row=dict(path=path,bytes=len(data),sha256=sha(data),second_read_exact=True)
            r['files'].append(row)
        r['all_providers'].append(dict(name=name,path=path,sha256=row['sha256'],exact=True))
r.update(passed=True,utc=m.utc(),build_review_sha256=sha((k.parent/'video-phase-runtime199/build-review.json').read_bytes()))
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('All three actual physical probe providers pinned; read-only supplementary GDI capture')
