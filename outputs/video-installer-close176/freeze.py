"""Pin new runtime sources before preflight/bootstrap, then archive snapshots."""
import ast,shutil
from common import *
phase=sys.argv[1];assert phase in ['inputs','runtime']
dest=k/'frozen-inputs.json'
if phase=='inputs':
    assert not dest.exists()
    paths=list(k.glob('*-before-return-scope.txt'))+list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'sites.json',k/'scope-tests.json',k/'scope-tests002.json',k/'return-scope-tests.json',k/'api-scope-review.json',k/'site-disassembly.json',k/'pin-contract-tests.json',k/'pin-contract-tests002.json',k/'timing-interface.json',k/'gdi-probe.c',k/'DESIGN.md',k/'build-review.json',k/'artifacts/runner.exe',
        k/'artifacts/gdi-probe.exe',k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe',
        k.parent/'video-surface-history/Invoke-Exclusive.ps1']+[k/('fixture-'+case+'.json') for case in ['candidate001']]
    for p in paths:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in paths}
    for name,row in read(k/'sites.json')['binaries'].items():pins[row['path']]=row['sha256']
    pins.update(read(k/'sites.json')['dependency_pins'])
    save(dest,pins)
else:
    assert not (k/'runtime-frozen.json').exists()
    pins=read(dest)
    for name,digest in pins.items():assert sha(ws/name)==digest,name
    for case in ['candidate001']:
        p=k/case/'preflight.json';assert read(p)['passed'];pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
    save(k/'emulator-ready.json',dict(passed=True,scope='Five-sample functional helper validation; strict baseline error retained',physical_access=False))
    pins[str((k/'emulator-ready.json').relative_to(ws)).replace('\\','/')]=sha(k/'emulator-ready.json');save(dest,pins)
    for case in ['candidate001']:
        source=k/case/'source';source.mkdir(exist_ok=False)
        for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'frozen-inputs.json',k/'sites.json',k/'timing-interface.json',k/'gdi-probe.c',k/'DESIGN.md']:shutil.copyfile(p,source/p.name)
    save(k/'runtime-frozen.json',dict(passed=True,before_emulator_bootstrap=True,physical_access=False))
print('Five-sample source freeze:',phase)
