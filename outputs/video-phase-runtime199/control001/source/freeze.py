"""Freeze actual sources/providers/builds before bootstrap; single output guards."""
import ast,shutil
from common import *
phase=sys.argv[1];assert phase in ['inputs','runtime'];dest=k/'frozen-inputs.json'
if phase=='inputs':
 assert not dest.exists()
 paths=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.json'))+[k/'window_probe.inc',k/'gdi-probe.c',k/'DESIGN.md',k/'restart_gate.h',k/'xwnunused179.inf',k/'runner.c',k/'test-gate.c',k/'artifacts/runner.exe',k/'artifacts/gdi-probe.exe',k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe',k.parent/'video-surface-history/Invoke-Exclusive.ps1']
 build=k.parent/'video-phase-profile198'
 paths+=list(build.glob('*.py'))+list(build.glob('*.json'))+list(build.glob('*.patch'))+list((build/'display').glob('*'))+[build/'display/profile_math.h',build/'math-tests.c']
 paths+=[build/name/'artifacts/xwnown.dll' for name in ['control001','candidate001']]
 pins={}
 for p in paths:
  if p.suffix=='.py':ast.parse(p.read_text())
  pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
 for name,row in read(k/'sites.json')['binaries'].items():pins[row['path']]=row['sha256']
 pins.update(read(k/'sites.json')['dependency_pins']);save(dest,pins)
else:
 assert not (k/'runtime-frozen.json').exists();pins=read(dest)
 for n,h in pins.items():assert sha(ws/n)==h,n
 for name in ['control001','candidate001']:
  p=k/name/'preflight.json';assert read(p)['passed'];pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
 save(k/'emulator-ready.json',dict(passed=True,scope='Fresh matched115 OFF/ON normal181 state; same inherited emulator-only null policy, no setup/debugger/physical action',physical_access=False))
 p=k/'emulator-ready.json';pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p);save(dest,pins)
 for name in ['control001','candidate001']:
  source=k/name/'source';source.mkdir(exist_ok=False)
  for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'frozen-inputs.json',k/'sites.json',k/'gdi-probe.c',k/'restart_gate.h',k/'runner.c',k/'test-gate.c',k/'xwnunused179.inf',k/'DESIGN.md']:shutil.copyfile(p,source/p.name)
 save(k/'runtime-frozen.json',dict(passed=True,before_emulator_bootstrap=True,physical_access=False))
print('Fresh186 freeze:',phase)
