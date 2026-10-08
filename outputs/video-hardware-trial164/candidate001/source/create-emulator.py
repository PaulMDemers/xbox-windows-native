"""Create prospective helper-runtime sources with no driver/configuration changes."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-physical-diagnostic163'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(old/'diagnostic-review.json')['display_compatibility_passed']
assert read(k/'build-review.json')['passed']
for name in ['common.py','preflight.py','audit.py','supervise.py','check-leases.ps1','Run.ps1']:
    text=(old/name).read_text(encoding='utf-8').replace('vphys163','vphys164').replace('diagnostic163','hardware-trial164')
    if name in ['preflight.py','audit.py']:text=text.replace('xwnrps01/','xwnv164/')
    if name=='Run.ps1':text=text.replace('diagnostic-plan.json','emulator-ready.json')
    (k/name).write_text(text,encoding='utf-8')
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[
    k/'runner.c',k/'build-review.json',k/'runner-source-review.json',k/'artifacts/runner.exe',
    old/'diagnostic-review.json',old/'candidate001/audit.json',
    k.parent/'video-physical-rehearsal162/fixture-candidate001.json',
    k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe',
    k.parent/'video-surface-history/Invoke-Exclusive.ps1',
    k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe']}
(k/'frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print('Fresh namespace runtime sources created; no guest launched')
