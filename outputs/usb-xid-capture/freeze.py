"""Freeze reviewed native hardware inputs; no console contact or automatic launch."""
import ast,datetime,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text())
assert not (k/'freeze.json').exists()
assert shutil.disk_usage('C:/').free>=20*1024**3
assert read(k/'emulator-review.json')['passed']
for name in ['parser-tests.json','guard-tests.json','tail-tests.json','hardware-tests.json','build003-review.json','build004-review.json']:assert read(k/name)['passed']
assert read(k/'build003-review.json')['main_sha256']==read(k/'build004-review.json')['main_sha256']
for name in ['usb_core_guarded.c','ohci_guarded.c']:assert (k/'artifacts/build003'/name).read_bytes()==(k/'artifacts/build004'/name).read_bytes()
files={}
for p in k.iterdir():
 if p.suffix in ['.py','.ps1','.c'] or p.name.endswith(('-review.json','-tests.json')) or p.name=='DESIGN.md':
  if p.suffix=='.py':ast.parse(p.read_text())
  files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in [k/'artifacts/build004/bin/default.xbe',k/'artifacts/build004/main.c',k/'artifacts/build004/usb_core_guarded.c',k/'artifacts/build004/ohci_guarded.c',k/'artifacts/build004/link.map']:
 files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(k/'freeze.json').write_text(json.dumps(dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,physical_access=False,authorized_next_step='One native capture under new successor ticket; no Windows boot or baseline writes.'),indent=2)+'\n')
print('Frozen',len(files),'inputs; hardware not launched')
