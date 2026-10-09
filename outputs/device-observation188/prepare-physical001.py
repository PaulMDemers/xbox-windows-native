"""Freeze reviewed successful diagnostic for startup-only physical observation; no network action."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'physical-ready.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(k/'emulator001/audit.json');assert a['diagnostic_usable'] and read(k/'emulator001/closure.json')['closed']
assert read(k/'protocol-tests.json')['passed']
for p in k.glob('*.py'):ast.parse(p.read_text())
files=[k/n for n in ['physical.py','prepare-physical.py','test-protocol.py','protocol-tests.json','analyze.py','atomic_json.py','probe003.c','build-review.json','artifacts/build003/observer.exe','emulator001/audit.json','emulator001/closure.json']]
files += [k.parent/'fatx0098-soak3/physical.py',k.parent/'video-word-physical187/capture.json',k.parent/'video-word-physical187/control001/restored-verification.json']
assert read(files[-1])['passed']
dest.write_text(json.dumps(dict(prepared=True,physical_qualified=False,launch_performed=False,
    pins={p.relative_to(ws).as_posix():sha(p) for p in files+[k/'audit-physical.py',k/'common.py',k.parent/'native-windows-physical-f/decode-legacy-events.py']},
    writes='Unique /F/xwnobs188a helper and normal-startup backup; startup command only. No registry, driver, service, mode or UI changes. Observer exits after five samples/120 seconds. User normal restart required.',
    gates='Current dashboard/keyboard report and baseline ownership/hash checks before launch; record request before sending; startup restored first on collect. Unknown replies never retried.'),indent=2)+'\n')
print('Startup-only physical188 protocol frozen; NOT launched')
