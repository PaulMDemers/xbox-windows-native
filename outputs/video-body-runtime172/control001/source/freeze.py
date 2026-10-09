"""Pin new runtime sources before preflight/bootstrap, then archive snapshots."""
import ast,shutil
from common import *
phase=sys.argv[1];assert phase in ['inputs','runtime']
dest=k/'frozen-inputs.json'
if phase=='inputs':
    assert not dest.exists()
    paths=list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'gdi-probe.c',k/'DESIGN.md',k/'build-review.json',k/'artifacts/runner.exe',
        k/'artifacts/gdi-probe.exe',k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe',
        k.parent/'video-surface-history/Invoke-Exclusive.ps1']+[k/('fixture-'+case+'.json') for case in ['control001','candidate001']]
    for p in paths:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    paths += [k.parent/'video-body-timing170'/v for v in ['driver-review.json','build-report.json','source-review.json','0113-body-timing.patch','host-tests.json']]
    paths += list((k.parent/'video-body-timing170/display').iterdir())
    paths += [k.parent/'video-body-timing170'/case/'artifacts/xwnown.dll' for case in ['control001','candidate001']]
    save(dest,{str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in paths})
else:
    assert not (k/'runtime-frozen.json').exists()
    pins=read(dest)
    for name,digest in pins.items():assert sha(ws/name)==digest,name
    for case in ['control001','candidate001']:
        p=k/case/'preflight.json';assert read(p)['passed'];pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
    save(k/'emulator-ready.json',dict(passed=True,scope='Five-sample functional helper validation; strict baseline error retained',physical_access=False))
    pins[str((k/'emulator-ready.json').relative_to(ws)).replace('\\','/')]=sha(k/'emulator-ready.json');save(dest,pins)
    for case in ['control001','candidate001']:
        source=k/case/'source';source.mkdir(exist_ok=False)
        for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'frozen-inputs.json',k/'gdi-probe.c',k/'DESIGN.md']:shutil.copyfile(p,source/p.name)
    save(k/'runtime-frozen.json',dict(passed=True,before_emulator_bootstrap=True,physical_access=False))
print('Five-sample source freeze:',phase)
