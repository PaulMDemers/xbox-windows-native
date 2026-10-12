"""Freeze this distinct diagnostic and its inherited runtime/cold dependencies."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((k.parent/'hd-reservation301/emulator-frozen.json').read_text());pins={}
for n,h in old.items():
    if n.startswith('outputs/hd-reservation301/'):continue
    assert sha(ws/n)==h;pins[n]=h
paths=list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'plan.json',k/'host-tests.json',k/'candidate001/fixture.json',
     ws/'outputs/video-cache-handoff/process-layouts.json',ws/'outputs/native-windows-nt5-kernel/kernel-publics.json']
for p in paths:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
    pins[p.relative_to(ws).as_posix()]=sha(p)
dest.write_text(json.dumps(pins,indent=2)+'\n')
(k/'host-frozen.json').write_bytes((k.parent/'hd-reservation301/host-frozen.json').read_bytes())
print('Frozen',len(pins),'diagnostic inputs')
