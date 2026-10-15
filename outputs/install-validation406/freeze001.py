import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';assert not out.exists()
assert json.loads((K/'assembly003.json').read_text())['status']=='assembled-readback-verified'
paths=list(K.glob('*.py'))+list(K.glob('*.c'))+list(K.glob('*.ps1'))+[K/'assembly003.json',K/'review-imports001.json',W/'tools/fatx_names.py']
old=json.loads((W/'outputs/fresh-assembly405/emu006/frozen.json').read_text())
paths += [W/p for p in old if not p.startswith('outputs/fresh-assembly405/')]
paths += [W/'outputs/fresh-assembly405/writeio001.py',W/'outputs/fresh-assembly405/normal-stage006.py']
pins={}
for p in paths:
    b=p.read_bytes()
    if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
    pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
out.mkdir();(out/'frozen.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Frozen inputs',len(pins))
