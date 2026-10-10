"""Freeze final new runtime inputs before either sacrificial launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'frozen.json';assert not dest.exists()
deps=list(k.glob('*.py'))+list(k.glob('*.ps1'))+list(k.glob('*.c'))+[k/'review.json',k/'kernel-site-review.json']
for case in ['control001','candidate001']:
 deps += [k/('fixture-'+case+'.json'),ws/'outputs/video-boot-layout219/artifacts/build001'/case/'xboxbvid.dll']
deps += [k/'artifacts/probe.exe',k/'artifacts/trigger.sys',ws/'outputs/video-upload-runtime211/artifacts/F/winnt/system32/ntoskrnl.exe']
deps += [ws/p for p in ['outputs/video-upload-address/discover_kernel.py','outputs/native-windows-nt5-kernel/trace-entry.py','outputs/native-windows-nt5-kernel/kernel-publics.json','outputs/native-windows-prebuild/monitor_capture.py','outputs/fatx-mapped-eof/coldio.py','outputs/fatx-mapped-eof/allocation.py','outputs/native-windows-paint-save/prepare-fixture.py','outputs/setup-wizard-automation201/restore.py','outputs/native-windows-fatx-preflight/analyze.py','outputs/native-windows-physical-f/decode-legacy-events.py']]
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
dest.write_text(json.dumps({p.relative_to(ws).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in deps},indent=2)+'\n')
print('Runtime pins:',len(deps))
