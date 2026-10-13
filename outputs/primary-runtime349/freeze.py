"""Pin complete inherited host/parser closure and all new actual inputs, per fresh case."""
import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];case=sys.argv[1];assert case in ['control001','candidate001'];out=K/case;dest=out/'emulator-frozen.json';assert not dest.exists()
assert json.loads((out/'preparation.json').read_text())['prepared']
old=json.loads((K.parent/'stock-repeat339/emulator-frozen.json').read_text());paths=[W/n for n in old if not n.startswith('outputs/stock-repeat339/')]
paths+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[out/'fixture.json',out/'preparation.json',out/'before-allocation/allocation.json']
paths+=list((K.parent/'hd-phase344').glob('*.py'))+[K.parent/'hd-phase344/build-review001.json',K.parent/'hd-phase344/parser001.json',K.parent/'primary-copy348/build001.json',K.parent/'primary-copy348/binary-review001.json',K/'host-contract002.json']
paths+=list((K.parent/'primary-copy348').glob('*.py'))+[K.parent/'primary-copy348/host002.json',K.parent/'primary-copy348/probe/build-review001.json',K.parent/'primary-copy348/probe/build001.json',K/'parser001.json']
pins={}
for p in paths:
    data=p.read_bytes()
    if p.suffix=='.py':ast.parse(data.decode('utf-8-sig'))
    pins[p.relative_to(W).as_posix()]=hashlib.sha256(data).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',case,len(pins),'inputs')
