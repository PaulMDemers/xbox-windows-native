"""Freeze inherited349 closure and explicit new debugger dependencies once."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'candidate001';dest=out/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(K/'protocol-tests001.json')['passed'] and read(out/'preparation.json')['prepared']
old=read(K.parent/'primary-runtime349/candidate001/emulator-frozen.json')
pins={name:h for name,h in old.items() if not name.startswith('outputs/primary-runtime349/')}
pins.update(read(K/'sites002.json')['dependencies'])
for name,h in pins.items():assert sha(W/name)==h,name
paths=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'sites001.json',K/'sites002.json',K/'protocol-tests001.json',K/'source-review.json',out/'fixture.json',out/'preparation.json',out/'before-allocation/allocation.json']
for p in paths:
    if p.suffix=='.py':ast.parse(p.read_text())
    pins[p.relative_to(W).as_posix()]=sha(p)
f=read(out/'fixture.json')
providers=read(K/'provider-preflight001.json');assert providers['passed'] and providers['prepared_fixture_sha256']==f['fixture_sha256']
for name,m in read(K/'sites002.json')['modules'].items():assert providers['modules'][name]['sha256']==m['sha256'],name
pins[(K/'provider-preflight001.json').relative_to(W).as_posix()]=sha(K/'provider-preflight001.json')
dest.write_text(json.dumps(pins,indent=2)+'\n');print(len(pins),'inputs frozen')
