import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];case=sys.argv[1];assert case=='candidate001'
out=K/case;dest=out/'emulator-frozen.json';assert not dest.exists()
assert json.loads((out/'preparation.json').read_text())['prepared']
old=json.loads((K.parent/'memory-runtime355/candidate001/emulator-frozen.json').read_text())
paths=[W/n for n in old]
paths+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'host-contract003.json',K/'source-review.json',out/'fixture.json',out/'preparation.json',out/'before-allocation/allocation.json']
diag=K.parent/'bandwidth361'
paths+=list(diag.glob('*.py'))+list(diag.glob('*.h'))+list(diag.glob('*.c'))+list(diag.glob('*.json'))
paths+=list((diag/'probe').glob('*.c'))+list((diag/'probe').glob('*.h'))+list((diag/'probe').glob('*.json'))+list((diag/'probe').glob('*.py'))
paths+=list((K.parent/'memory-analysis360').glob('*.py'))
pins={}
for p in paths:
 data=p.read_bytes()
 if p.suffix=='.py':ast.parse(data.decode('utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=hashlib.sha256(data).hexdigest()
for n,h in old.items():assert pins[n]==h
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',len(pins),'inputs')
