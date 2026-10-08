"""Pin helper runtime sources and preflight before emulator bootstrap."""
import ast,shutil
from common import *
assert read(k/'candidate001/preflight.json')['passed'];p=k/'runtime-frozen.json';assert not p.exists()
pins=read(k/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
for path in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'candidate001/preflight.json',k/'emulator-ready.json']:
    if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8'))
    pins[str(path.relative_to(ws)).replace('\\','/')]=sha(path)
save(k/'frozen-inputs.json',pins)
source=k/'candidate001/source';source.mkdir(exist_ok=False)
for path in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'frozen-inputs.json']:shutil.copyfile(path,source/path.name)
save(p,dict(passed=True,before_emulator_bootstrap=True,source_pins=len(pins),physical_access=False))
