import json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from common import ColdIO,readers,sha,save
f=json.loads((k/'candidate002/fixture.json').read_text());source=pathlib.Path(f['fixture_path_linux']);assert sha(source)==f['fixture_sha256']
out=k/'artifacts/state-providers001';out.mkdir(exist_ok=False)
with ColdIO(source) as io:
    p=out/'psapi.dll';p.write_bytes(readers(io,source)['F'].read('winnt/system32/psapi.dll'))
save(k/'state-provider001.json',dict(source_sha256=f['fixture_sha256'],providers={'psapi.dll':sha(p)}))
