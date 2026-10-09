"""Pin own source and actual harness/reader/build/fixture dependencies before single launch."""
import ast
from common import *
dest=k/'frozen-inputs.json';assert not dest.exists()
assert read(k/'fixture-emulator001.json')['prepared'] and read(k/'build-review.json')['passed']
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
inputs=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))
inputs += [k/'artifacts/build003/observer.exe',k/'fixture-emulator001.json',k/'build-review.json']
inputs += [k.parent/v for v in ['video-surface-history/Invoke-Exclusive.ps1','native-windows-nt5-kernel/Invoke-Diagnostic.ps1','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py','native-windows-physical-f/decode-legacy-events.py','gpu-reset-banner152/ftp_deadline.py']]
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in inputs}
snap=k/'emulator001/source';snap.mkdir(exist_ok=False)
for p in inputs:
    if p.parent==k:(snap/p.name).write_bytes(p.read_bytes())
save(dest,pins);print('Pinned',len(pins),'actual sources/inputs; observer only; no debugger/UI actions')
