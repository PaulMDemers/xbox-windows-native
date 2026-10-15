import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';assert json.loads((out/'preparation.json').read_text())['prepared'];dest=out/'emulator-frozen.json';assert not dest.exists()
old=json.loads((W/'outputs/demo-runtime377/control001/emulator-frozen.json').read_text());paths=[W/n for n in old if not n.startswith('outputs/demo-runtime377/')]
paths+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'host-contract001.json',out/'fixture.json',out/'preparation.json',out/'before-allocation/allocation.json',W/'tools/xwn_image.py']
pins={}
for p in paths:
 b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',len(pins),'host inputs')
