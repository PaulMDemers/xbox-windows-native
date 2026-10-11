"""Read-only actual NT5 DLL evidence for installer dynamic exports."""
import json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from common import ColdIO,readers,sha,save,m
f=json.loads((k/'candidate002/fixture.json').read_text());source=pathlib.Path(f['fixture_path_linux']);assert sha(source)==f['fixture_sha256']
out=k/'artifacts/install-providers001';out.mkdir(exist_ok=False)
r=dict(source_sha256=f['fixture_sha256'],providers={})
with ColdIO(source) as io:
    rr=readers(io,source)
    for name in ['newdev.dll','cfgmgr32.dll','ntdll.dll']:
        p=out/name;p.write_bytes(rr['F'].read('winnt/system32/'+name));r['providers'][name]=sha(p)
save(k/'install-providers001.json',r)
