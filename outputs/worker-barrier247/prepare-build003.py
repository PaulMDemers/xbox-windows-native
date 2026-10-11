"""Retain002 path preparation failure; selective fresh003 parent/output pins."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;assert not (k/'build003.py').exists()
(k/'build002.json').write_text(json.dumps(dict(passed=False,build_invoked=False,guest_launch=False,source_change_observed=False,error='Broad output renaming selected nonexistent246 candidate002 parent manifest; failed before original-source reads or capsule creation',source_sha256=hashlib.sha256((k/'build002.py').read_bytes()).hexdigest()),indent=2)+'\n')
s=(k/'build.py').read_text().replace("dest=k/'build001.json'","dest=k/'build003.json'").replace('phase247-build001','phase247-build003').replace("k/'candidate001-source-pins.json'","k/'candidate003-source-pins.json'").replace('delta001.patch','delta003.patch')
(k/'build003.py').write_text(s)
for name in ['Run.ps1','freeze.py']:
 p=k/name;p.write_text(p.read_text().replace('artifacts/build002','artifacts/build003').replace('build002.json','build003.json'))
(k/'Build003.ps1').write_text((k/'Build002.ps1').read_text().replace('/build002.py','/build003.py'))
print('003 selective parent pins prepared, no old build replay')
