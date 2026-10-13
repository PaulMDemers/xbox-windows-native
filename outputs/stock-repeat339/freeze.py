"""Freeze new repeat-boot sources and inherited host/parser dependencies."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'emulator-frozen.json';assert not dest.exists()
assert json.loads((K/'emu001/preparation.json').read_text())['prepared']
old=json.loads((K.parent/'stock-runtime335/emulator-frozen.json').read_text())
paths=[W/n for n in old if not n.startswith('outputs/stock-runtime335/')]
paths+=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[K/'emu001/fixture.json',K/'emu001/preparation.json']
paths+=list((K.parent/'stock-focus338').glob('*.py'))+list((K.parent/'stock-focus338').glob('*.h'))+list((K.parent/'stock-focus338').glob('*.inc'))+list((K.parent/'stock-focus338').glob('*.c'))+[K.parent/'stock-focus338/build-review001.json']
pins={}
for p in paths:
    b=p.read_bytes()
    if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
    pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',len(pins),'repeat boot dependencies')
