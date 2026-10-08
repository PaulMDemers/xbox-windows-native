"""Freeze final helper validation inputs before bootstrap or Windows launch."""
import ast,shutil
from common import *
dest=k/'emulator-ready.json';assert not dest.exists();assert read(k/'candidate001/preflight.json')['passed']
pins=read(k/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'fixture-candidate001.json',k/'candidate001/preflight.json',k/'DESIGN.md']:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
save(k/'frozen-inputs.json',pins)
source=k/'candidate001/source';source.mkdir(exist_ok=False)
for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'runner.c',k/'DESIGN.md',k/'frozen-inputs.json']:
    shutil.copyfile(p,source/p.name)
save(dest,dict(passed=True,sources=len(pins),physical_access=False,strict_gates_unchanged=True,
              pending='Single helper namespace emulator runtime before physical diagnostic'))
