import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu002';assert not out.exists()
assert json.loads((K/'assembly002.json').read_text())['status']=='assembled-readback-verified'
paths=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'assembly002.json']
old=json.loads((W/'outputs/install-validation406/emu001/frozen.json').read_text())
paths += [W/p for p in old]
paths += [W/'outputs/crypto-persistence423/results.py',W/'outputs/crypto-persistence423/probe.c',W/'outputs/crypto-persistence423/build001.json']
pins={}
for p in paths:
 b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
out.mkdir();(out/'frozen.json').write_text(json.dumps(pins,indent=2)+'\n');print('Frozen inputs',len(pins))
