"""Create fresh reverse-order diagnostic; never reuse185 stage records."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

k = Path(__file__).resolve().parent
ws = k.parents[1]
old = k.parent / 'video-word-runtime185'
assert not (k / 'creation.json').exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert read(old / 'evidence-review.json')['passed']
for case in ['control001', 'candidate001']:
    assert read(old / case / 'closure.json')['closed']

names = ['Build-Probe001.ps1', 'Run.ps1', 'atomic_json.py', 'audit-package.py',
         'audit.py', 'check-leases.ps1', 'close-emulator.py', 'common.py',
         'dib_analysis.py', 'freeze.py', 'gdi-probe.c', 'inventory-devices.py',
         'preflight.py', 'prepare-parent.py', 'prepare.py', 'restart_gate.h',
         'review-build.py', 'review-evidence.py', 'review-pair.py', 'runner.c',
         'sample_analysis.py', 'sites.json', 'supervise.py', 'test-gate.c',
         'validate-inputs.py', 'xwnunused179.inf']
sources = {}
for name in names:
    p = old / name
    text = p.read_text(encoding='utf-8')
    text = text.replace('video-word-runtime185', 'video-word-order186')
    text = text.replace('word185', 'word186').replace('xwnws185', 'xwnws186')
    for label in ['Closed185','Fresh185','New185','185 inputs']:
        text = text.replace(label,label.replace('185','186'))
    if name in ['prepare.py', 'Run.ps1', 'audit.py', 'audit-package.py',
                'close-emulator.py', 'supervise.py', 'review-evidence.py']:
        text = text.replace('video-word-runtime186', 'video-word-order186')
    if name == 'Run.ps1':
        text = text.replace("if($Case -eq 'candidate001')", "if($Case -eq 'control001')")
        text = text.replace("'control001/audit.json'", "'candidate001/audit.json'")
        text = text.replace('Control diagnostic prerequisites failed',
                            'Candidate diagnostic prerequisites failed')
    if name == 'gdi-probe.c':
        text = text.replace('count<2000', 'count<20000')
        text = text.replace('"XWN_GDI_PROBE_VERSION",7', '"XWN_GDI_PROBE_VERSION",8')
        text = text.replace('XwnGdiProbeV7', 'XwnGdiProbeV8')
        text = text.replace('scalar row stores115 - Esc cancels',
                            'scalar row stores115 longer - Esc cancels')
    if name == 'sample_analysis.py':
        text = text.replace('v7', 'v8').replace("'7','256','128'", "'8','256','128'")
        text = text.replace('1<=v[2]<=2000 and 0<v[3]<=181000',
                            '1<=v[2]<=20000 and 1500<=v[3]<=181000')
    if name == 'review-build.py':
        text = text.replace('v7 ExtEscape', 'v8 ExtEscape')
        text = text.replace('driver_changed=True', 'driver_changed=False')
    if name == 'review-pair.py':
        text = text.replace('control then candidate', 'candidate then control')
        text = text.replace('coarse GetTickCount elapsed per operation',
                            'coarse GetTickCount elapsed per operation, each loop>=1500ms')
    if name == 'review-evidence.py':
        text = text.replace('Two ordered emulator boots',
                            'Two reverse-order longer-interval emulator boots')
    if name.endswith('.py'):
        ast.parse(text)
    (k / name).write_text(text, encoding='utf-8', newline='\n')
    if name in ['runner.c', 'restart_gate.h', 'test-gate.c', 'xwnunused179.inf', 'sites.json']:
        (k / name).write_bytes(p.read_bytes())
    sources[name] = dict(prior_sha256=sha(p), new_sha256=sha(k / name))

assert (k / 'generation001-refusal.json').exists()
(k / 'artifacts').mkdir(exist_ok=True)
shutil.copyfile(old / 'artifacts/runner.exe', k / 'artifacts/runner.exe')
assert sha(k / 'artifacts/runner.exe') == sha(old / 'artifacts/runner.exe')
for name in ['runner.c', 'restart_gate.h', 'test-gate.c', 'xwnunused179.inf']:
    assert (k / name).read_bytes() == (old / name).read_bytes(), name
r = dict(created=True, prior_evidence_sha256=sha(old / 'evidence-review.json'),
         sources=sources, generation=2, preserved_refusal_sha256=sha(k / 'generation001-refusal.json'), drivers_changed=False, guest_launch=False,
         physical_access=False, order=['candidate001', 'control001'],
         measured_loop_minimum_ms=1500, operation_cap=20000,
         reason='185 unchanged readback also faster; short intervals/order confound attribution.')
(k / 'creation.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print('Fresh186 reverse-order kit created; no prior outputs/fixtures reused')
