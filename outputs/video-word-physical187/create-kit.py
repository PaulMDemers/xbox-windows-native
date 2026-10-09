"""Fresh physical187 sources; no access, stage reuse or numeric replacement."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
k = Path(__file__).resolve().parent
old = k.parent / 'video-paired-timing166'
emu = k.parent / 'video-word-order186'
dest = k / 'creation.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert read(emu / 'evidence-review.json')['passed']
assert read(emu / 'order-comparison.json')['passed']
for case in ['control001', 'candidate001']:
    assert read(emu / case / 'closure.json')['closed']
    (k / case).mkdir(exist_ok=False)
(k / 'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe', 'gdi-probe.exe']:
    shutil.copyfile(emu / 'artifacts' / name, k / 'artifacts' / name)
for name in ['sample_analysis.py', 'dib_analysis.py', 'runner.c', 'gdi-probe.c',
             'restart_gate.h', 'test-gate.c']:
    shutil.copyfile(emu / name, k / name)
for name in ['capture.py', 'review.py', 'edit-binding.py']:
    p = k.parent / 'video-physical-review159' / name
    text = p.read_text(encoding='utf-8')
    if name == 'capture.py':
        text = text.replace('current-display-rollback159.zip', 'current-display-rollback187.zip')
        text = text.replace("paths += ['/E/", "paths += ['/F/winnt/system32/config/default','/F/winnt/system32/config/sam','/F/winnt/system32/config/security','/F/winnt/system32/win32k.sys','/E/")
    ast.parse(text)
    (k / name).write_text(text, encoding='utf-8', newline='\n')
r = dict(created=True, emulator_evidence_sha256=sha(emu / 'evidence-review.json'),
         order_comparison_sha256=sha(emu / 'order-comparison.json'),
         runner_sha256=sha(k / 'artifacts/runner.exe'),
         probe_sha256=sha(k / 'artifacts/gdi-probe.exe'),
         physical_access=False, launch_performed=False, policy_change=False)
dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print('Fresh187 hardware capture/proposal sources and exact helpers prepared')
