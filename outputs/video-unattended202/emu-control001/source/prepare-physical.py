"""Freeze exact physical202 OFF/ON proposal after matched emulator scopes and201 hardware Cancel."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'physical-ready.json';assert not dest.exists()
for name in ['capture.json','binding-review.json','binding-edit.json','package-review.json','build-review.json','probe-providers.json','parser-tests.json','emulator-pair-review.json']:
    assert read(k/name)['passed'],name
prior=k.parent/'setup-wizard-automation201/physical001';assert read(prior/'review.json')['passed'] and read(prior/'closure.json')['closed']
for case in ['control001','candidate001']:
    a=read(k/('emu-'+case)/'audit.json');assert a['scoped_display_passed'] and a['integrity_passed']
for name,digest in read(k/'parser-tests.json')['source_pins'].items():assert sha(k/name)==digest
files=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
inputs=[k/name for name in ['capture.json','binding-review.json','binding-edit.json','package-review.json','build-review.json','probe-providers.json','parser-tests.json','emulator-pair-review.json','artifacts/proposed-system','artifacts/runner.exe','artifacts/gdi-probe.exe','artifacts/wizard.exe']]
inputs += [k/('emu-'+case)/name for case in ['control001','candidate001'] for name in ['audit.json','closure.json']]
inputs += [ws/row['source'] for rows in read(k/'package-review.json')['cases'].values() for row in rows]
inputs += [prior/'review.json',prior/'closure.json',k.parent/'fatx0098-soak3/physical.py',k.parent/'native-windows-physical-f/decode-legacy-events.py']
expected=read(k.parent/'video-phase-physical200/physical-ready.json')['documented_physical_warning_signatures']
result=dict(prepared=True,physical_qualified=False,source_pins={p.name:sha(p) for p in files},input_pins={p.relative_to(ws).as_posix():sha(p) for p in inputs},
 documented_physical_warning_signatures=expected,
 limits='Known cancellation child joined before unchanged194 idle/measurement/restart. Same198 profileOFF/ON display providers/scalarOFF, exact199 probe. No unknown dialog/device disabling or strict warning waiver. Current rollback restored after each boot. Candidate only after scoped control, typed hives, documented warnings and restoration.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('Physical202 exact proposal/protocol frozen; not launched')
