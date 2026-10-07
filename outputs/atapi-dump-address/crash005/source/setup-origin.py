"""Create a new, unchanged-driver diagnostic from the closed crash004 kit."""
from pathlib import Path

k = Path(__file__).resolve().parent
source = k.parent / 'dump-lba-trace'
names = ['trigger.c', 'probe.c', 'Build.ps1', 'review.py', 'build-review.json',
         'hal-review.json', 'fatx-review.json', 'nvnet-review.json', 'layouts.json',
         'kernel-review.json', 'atomic_json.py', 'modules.json', 'modules-review.py',
         'common.py', 'configuration.py', 'cold-map.py', 'prepare.py', 'Run.ps1',
         'preflight.py', 'supervise.py', 'record-closure.py', 'audit-crash.py',
         'trace.py', 'verify.py', 'analyze-wire.py', 'Invoke-Lba.ps1']
for name in names:
    target = k / name
    assert not target.exists(), name
    data = (source / name).read_bytes()
    if name.endswith(('.py', '.ps1')) and name not in ['Build.ps1', 'review.py']:
        data = data.replace(b'dump-lba-trace', b'atapi-dump-address').replace(b'crash004', b'crash005')
    target.write_bytes(data)
(k / 'artifacts').mkdir(exist_ok=False)
for name in ['probe.exe', 'trigger.sys']:
    (k / 'artifacts' / name).write_bytes((source / 'artifacts' / name).read_bytes())
print('Created unique crash005 kit. No preparation or launch performed.')
