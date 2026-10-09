"""Freeze new190 runtime inputs and exact source snapshots before any guest launch."""
import ast
from common import *
dest=k/'frozen-inputs.json';assert not dest.exists()
for case in ['pending001','idle001']:assert read(k/('fixture-'+case+'.json'))['prepared']
inputs=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
inputs += [k/'DESIGN.md',k/'build-review.json',k/'artifacts/runner.exe',k.parent/'video-word-order186/artifacts/gdi-probe.exe',k.parent/'xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe']
inputs += [k/('fixture-'+case+'.json') for case in ['pending001','idle001']]
inputs += [k/'parents.json',k.parent/'video-setup-preflight190/build-review.json']
inputs += [k.parent/v for v in ['video-surface-history/Invoke-Exclusive.ps1','native-windows-nt5-kernel/Invoke-Diagnostic.ps1','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py','native-windows-physical-f/decode-legacy-events.py','gpu-reset-banner152/ftp_deadline.py']]
for p in inputs:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
pins={str(p.relative_to(ws)).replace('\\','/'):sha(p) for p in inputs}
for case in ['pending001','idle001']:
    snapshot=k/case/'source';snapshot.mkdir(exist_ok=False)
    for p in inputs:
        if p.parent==k:(snapshot/p.name).write_bytes(p.read_bytes())
save(dest,pins);print('190 exact sources, fixtures, binaries and harness/reader dependencies frozen')
