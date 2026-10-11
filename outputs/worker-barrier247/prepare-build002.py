"""Preserve pre-write permission failure; fresh root-owned source build002."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
assert not (k/'build002.py').exists() and not (k/'build001.json').exists()
r=dict(passed=False,failed_before_first_source_write=True,source_path='/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/hw/xbox/nv2a/nv2a.c',error='WSL default paul user denied root-owned source write; finally same denial before record publication',build_invoked=False,guest_launch=False,source_sha256=hashlib.sha256((k/'build.py').read_bytes()).hexdigest(),source_change_observed=False,scope='First open failed before truncation; no compile or guest. Empty unique phase247-build001 capsule preserved.')
(k/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
s=(k/'build.py').read_text().replace('build001','build002').replace('candidate001-source-pins','candidate002-source-pins').replace('delta001.patch','delta002.patch')
# Parent is still the verified246 build001 capsule, never a failed247 capsule.
s=s.replace("prior/'artifacts/build002/source'","prior/'artifacts/build001/source'")
(k/'build002.py').write_text(s)
for name in ['Run.ps1','freeze.py']:
 p=k/name;p.write_text(p.read_text().replace('artifacts/build001','artifacts/build002').replace('build001.json','build002.json'))
s=(k/'Build.ps1').read_text().replace('wsl -e','wsl -u root -e').replace('/build.py','/build002.py')
(k/'Build002.ps1').write_text(s)
print('Unique build002 prepared; failed001 retained')
