"""Pin complete inherited host/parser closure and all new actual inputs, per fresh case."""
import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];case=sys.argv[1];assert case in ['control001','candidate001'];out=K/case;dest=out/'emulator-frozen.json';assert not dest.exists()
assert json.loads((out/'preparation.json').read_text())['prepared']
old=json.loads((K.parent/'stock-repeat339/emulator-frozen.json').read_text());paths=[W/n for n in old if not n.startswith('outputs/stock-repeat339/')]
paths+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[out/'fixture.json',out/'preparation.json',out/'before-allocation/allocation.json']
paths+=list((K.parent/'hd-phase344').glob('*.py'))+[K.parent/'hd-phase344/build-review001.json',K.parent/'hd-phase344/parser001.json',K.parent/'eligible-copy351/build001.json',K.parent/'eligible-copy351/binary-review001.json',K/'host-contract002.json']
paths+=list((K.parent/'eligible-copy351').glob('*.py'))+[K.parent/'eligible-copy351/host001.json',K.parent/'eligible-copy351/probe/build-review001.json',K.parent/'eligible-copy351/probe/build001.json',K/'parser001.json']
paths += [K/'protocol001.json',K.parent/'eligible-copy351/source-review001.json']
paths += list((K.parent/'eligible-copy351').glob('*.h')) + list((K.parent/'eligible-copy351').glob('*.c'))
paths += list((K.parent/'eligible-copy351/probe').glob('*.c')) + list((K.parent/'eligible-copy351/probe').glob('*.h'))
pins={}
for p in paths:
    data=p.read_bytes()
    if p.suffix=='.py':ast.parse(data.decode('utf-8-sig'))
    pins[p.relative_to(W).as_posix()]=hashlib.sha256(data).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',case,len(pins),'inputs')
