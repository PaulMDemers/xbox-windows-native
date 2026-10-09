"""Freeze this new202 runner/helpers/parsers/providers and two fresh fixtures; no launch."""
import ast,shutil
from common import *
dest=k/'emulator-frozen.json';assert not dest.exists()
assert read(k/'build-review.json')['passed'] and read(k/'parser-tests.json')['passed']
paths=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+list(k.glob('*.h'))
paths += [k/n for n in ['build-review.json','build001.json','parser-tests.json','artifacts/runner.exe','artifacts/replay.exe','artifacts/wizard.exe','fixture-control001.json','fixture-candidate001.json']]
paths += [k.parent/n for n in ['video-surface-history/Invoke-Exclusive.ps1','native-windows-nt5-kernel/Invoke-Diagnostic.ps1','fatx-mapped-eof/coldio.py','fatx-mapped-eof/allocation.py','native-windows-paint-save/prepare-fixture.py','native-windows-physical-f/decode-legacy-events.py','gpu-reset-banner152/ftp_deadline.py']]
paths += [ws/row['source'] for rows in read(k.parent/'video-phase-physical200/package-review.json')['cases'].values() for row in rows]
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
pins={p.relative_to(ws).as_posix():sha(p) for p in paths}
for case in ['control001','candidate001']:
    f=read(k/('fixture-'+case+'.json'));assert f['prepared'] and not f['inherited_null_policy']
    snap=k/('emu-'+case)/'source';snap.mkdir(exist_ok=False)
    for p in paths:
        if p.parent==k:shutil.copyfile(p,snap/p.name)
save(dest,pins);print('New202 emulator sources/fixtures frozen:',len(pins),'inputs')
