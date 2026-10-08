"""Complete prospective diagnostic source snapshot before launching."""
import ast,shutil
from common import *
dest=k/'runtime-frozen.json';assert not dest.exists()
assert read(k/'candidate001/preflight.json')['passed']
pins=read(k/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'DESIGN.md',k/'diagnostic-plan.json',k/'candidate001/preflight.json']:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
save(k/'frozen-inputs.json',pins)
source=k/'candidate001/source';source.mkdir(exist_ok=False)
for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'DESIGN.md',k/'diagnostic-plan.json',k/'frozen-inputs.json']:
    shutil.copyfile(p,source/p.name)
save(dest,dict(passed=True,source_pins=len(pins),strict_qualification_unchanged=True,physical_access=False,
              seed_sha256=read(k/'fixture-candidate001.json')['seed_sha256']))
print('Nonpromoting sources frozen; original strict gates unchanged')
