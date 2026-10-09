"""Freeze one new diagnostic and selected-monitor dependencies; no guest launch."""
import ast
from common import *

dest = k / 'frozen-inputs.json'
assert not dest.exists() and read(k / 'fixture-pending002.json')['prepared']
inputs = list(k.glob('*.py')) + list(k.glob('*.ps1')) + [k / 'DESIGN.md', k / 'fixture-pending002.json', k / 'system-forensics.json']
inputs += [k.parent / 'video-measurement-boundary194' / name for name in ['frozen-inputs.json', 'fixture-pending001.json', 'build-review.json', 'pending001/audit.json', 'pending001/closure.json']]
inputs += [k.parent / name for name in ['native-windows-prebuild/monitor_capture.py', 'native-windows-nt5-kernel/trace-entry.py',
    'video-surface-history/Invoke-Exclusive.ps1', 'native-windows-nt5-kernel/Invoke-Diagnostic.ps1', 'fatx-mapped-eof/coldio.py',
    'fatx-mapped-eof/allocation.py', 'native-windows-paint-save/prepare-fixture.py', 'gpu-reset-banner152/ftp_deadline.py',
    'native-windows-physical-f/decode-legacy-events.py']]
for p in inputs:
    if p.suffix == '.py':
        ast.parse(p.read_text(encoding='utf-8'))
snapshot = k / 'pending002/source'
snapshot.mkdir(exist_ok=False)
for p in inputs:
    if p.parent == k:
        (snapshot / p.name).write_bytes(p.read_bytes())
save(dest, {p.relative_to(ws).as_posix(): sha(p) for p in inputs})
print('196 exact standalone/source/reader/monitor inputs frozen, no launch')
