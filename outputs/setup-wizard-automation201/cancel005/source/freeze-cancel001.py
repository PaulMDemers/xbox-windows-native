"""Freeze actual201 sources and providers before this unique passive run."""
import ast
from common import *
dest=k/'frozen-cancel001.json';assert not dest.exists()
assert read(k/'fixture-cancel001.json')['prepared'] and read(k/'build-review.json')['passed']
assert read(k/'guardian-review.json')['passed'] and read(k/'analysis-tests.json')['passed']
inputs=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
inputs += [k/'artifacts/build001/wizard.exe',k/'fixture-cancel001.json',k/'build-review.json',k/'build001.json',k/'policy-tests.json',k/'guardian-review.json',k/'analysis-tests.json',k/'guardian-build002.json',k/'artifacts/guardian002/guardian.exe']
inputs += [k.parent/v for v in ['video-surface-history/Invoke-Exclusive.ps1','native-windows-nt5-kernel/Invoke-Diagnostic.ps1','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py','native-windows-physical-f/decode-legacy-events.py','gpu-reset-banner152/ftp_deadline.py']]
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in inputs}
snap=k/'cancel001/source';snap.mkdir(exist_ok=False)
for p in inputs:
    if p.parent==k:(snap/p.name).write_bytes(p.read_bytes())
save(dest,pins);print('Frozen201 cancel001:',len(pins),'actual inputs; Known explicit Cancel + genuine restart guards only')
