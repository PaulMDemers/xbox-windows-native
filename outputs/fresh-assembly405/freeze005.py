import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu005'
assert not out.exists();assert json.loads((K/'assembly004.json').read_text())['status']=='assembled-readback-verified'
out.mkdir()
paths=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'assembly004.json',K/'before-allocation/allocation.json']
old=json.loads((W/'outputs/release-readiness403/emu001/emulator-frozen.json').read_text())
paths += [W/p for p in old if not p.startswith('outputs/release-readiness403/')]
pins={}
for p in paths:
    b=p.read_bytes()
    if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
    pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
(out/'frozen.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Frozen host inputs',len(pins))
