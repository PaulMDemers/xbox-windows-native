"""Create recovery tooling only; preparation requires successful crash evidence."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'atapi-lba48-network';new=k.parent/'atapi-lba48-recovery'
assert not new.exists();new.mkdir();(new/'artifacts').mkdir()
for name in ['common.py','atomic_json.py','configuration.py','cold-map.py','supervise.py','record-closure.py','Run.ps1']:
    data=(old/name).read_bytes().replace(b'atapi-lba48-network',b'atapi-lba48-recovery')
    if name!='common.py':
        data=data.replace(b"['control001','candidate001']",b"['recovery003']").replace(b"'control001','candidate001'",b"'recovery003'").replace(b"$Case='control001'",b"$Case='recovery003'")
        data=data.replace(b"['mode0','mode0b','recovery003']",b"['recovery003']")
    if name=='Run.ps1':data=data.replace(b'(Join-Path $PSScriptRoot Invoke-Network.ps1)',b'(Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1)')
    (new/name).write_bytes(data)
for name in ['recovery-probe.c','Build-Recovery.ps1','toolchain-review.json']:(new/name).write_bytes((k/name).read_bytes())
(new/'artifacts/recovery-probe.exe').write_bytes((k/'artifacts/recovery-probe.exe').read_bytes())
(new/'setup-origin.py').write_bytes(Path(__file__).read_bytes())
print('Recovery tooling copied; no child created or booted.')
