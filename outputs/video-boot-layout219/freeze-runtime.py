"""Freeze complete new219 runtime sources and immutable private inputs, no launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(k/'native-input-review.json')['passed'] and read(k/'build-review.json')['passed']
paths=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.h'))+[k/n for n in ['build001.json','build-review.json','source-review.json','host-tests002.json','native-input-review.json','runtime-provenance.json','fixture-control001.json','fixture-candidate001.json','patch-review002.json','boot-layout219-002.patch']]
paths += [k/'artifacts/build001'/case/'xboxbvid.dll' for case in ['control001','candidate001']]
paths += [ws/n for n in ['outputs/video-upload-runtime211/build-review.json','outputs/video-upload-runtime211/fixture-candidate001.json','outputs/setup-wizard-automation201/restore.py','outputs/fatx-mapped-eof/coldio.py','outputs/fatx-mapped-eof/allocation.py','outputs/native-windows-paint-save/prepare-fixture.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/gpu-reset-banner152/ftp_deadline.py','outputs/native-windows-prebuild/monitor_capture.py','outputs/native-windows-nt5-kernel/kernel-publics.json','outputs/fatx-cache-buffer/sites.json']]
paths += [ws/'outputs/video-upload-runtime211/artifacts'/name for name in ['runner.exe','replay.exe','wizard.exe']]
for p in paths:
    if p.suffix=='.py':ast.parse(p.read_text())
pins={p.relative_to(ws).as_posix():sha(p) for p in paths};dest.write_text(json.dumps(pins,indent=2)+'\n')
print('Frozen219 ordinary/runtime-observation inputs:',len(pins))
