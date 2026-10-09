"""Freeze actual201 sources and providers before this unique targeted cancellation run."""
import ast
from common import *
dest=k/'frozen-cancel003.json';assert not dest.exists()
assert read(k/'fixture-cancel003.json')['prepared'] and read(k/'build-review002.json')['passed']
assert read(k/'guardian-review003.json')['passed'] and read(k/'analysis-tests002.json')['passed']
inputs=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
inputs += [k/'artifacts/build002/wizard.exe',k/'fixture-cancel003.json',k/'build-review002.json',k/'build002.json',k/'policy-tests.json',k/'guardian-review003.json',k/'analysis-tests002.json',k/'review-observer-path003.json',k/'guardian-build003.json',k/'artifacts/guardian003/guardian.exe']
inputs += [k.parent/'device-observation188/artifacts/build003/observer.exe',k.parent/'device-observation188/build-review.json',k.parent/'device-observation188/probe003.c',k.parent/'device-observation188/analyze.py']
inputs += [k.parent/v for v in ['video-surface-history/Invoke-Exclusive.ps1','native-windows-nt5-kernel/Invoke-Diagnostic.ps1','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py','native-windows-physical-f/decode-legacy-events.py','gpu-reset-banner152/ftp_deadline.py']]
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in inputs}
snap=k/'cancel003/source';snap.mkdir(exist_ok=False)
for p in inputs:
    if p.parent==k:(snap/p.name).write_bytes(p.read_bytes())
save(dest,pins);print('Frozen201 cancel003:',len(pins),'actual inputs; Known explicit Cancel + genuine restart guards only')
