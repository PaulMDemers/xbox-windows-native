"""Fresh successor; preserve168 frozen address-assumption failure unchanged."""
import ast,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-process-lifecycle168'
assert not (k/'Run.ps1').exists()
for p in list(old.glob('*.py'))+list(old.glob('*.ps1'))+[old/'sites.json',old/'timing-interface.json',old/'gdi-probe.c',old/'DESIGN.md',old/'build-review.json']:
 if p.name=='create-kit.py':continue
 data=p.read_text(encoding='utf-8').replace('video-process-lifecycle168','video-process-lifecycle169').replace('vlife168','vlife169').replace('xwnvl168','xwnvl169')
 if p.suffix=='.py':ast.parse(data)
 (k/p.name).write_bytes(data.encode('utf-8'))
(k/'artifacts').mkdir(exist_ok=False)
for n in ['runner.exe','gdi-probe.exe','umpnpmgr.dll']:shutil.copyfile(old/'artifacts'/n,k/'artifacts'/n)
print('Fresh169 kit; no guest/fixture launch,168 preserved')
