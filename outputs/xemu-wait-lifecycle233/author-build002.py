"""Preserve preliminary build001; author corrected fresh build002 and selection."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'build-selection002.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();changed={}
s=(k/'build.py').read_text().replace('from patch import apply','from patch002 import apply')
s=s.replace("dest=k/'build001.json'","dest=k/'build002.json'").replace("sha(k/'patch.py')","sha(k/'patch002.py')")
s=s.replace("art=k/'artifacts/build001'","art=k/'artifacts/build002'")
s=s.replace("(k/'candidate001-source-pins.json')","(k/'candidate002-source-pins.json')")
s=s.replace('wait233-build001.patch','wait233-build002.patch').replace("logs/'candidate002.log'","logs/'build002.log'")
p=k/'build002.py';assert not p.exists();p.write_text(s)
s=(k/'Build.ps1').read_text().replace('/build.py','/build002.py');(k/'Build002.ps1').write_text(s)
for name in ['Run.ps1','freeze.py']:
    p=k/name;before=p.read_bytes();s=p.read_text().replace('build001.json','build002.json').replace('artifacts/build001','artifacts/build002')
    p.write_text(s);changed[name]=dict(before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=sha(p))
dest.write_text(json.dumps(dict(selected='build002',preliminary_build001_preserved=True,host_mask_test001_failed=True,changed_before_freeze=changed,physical_access=False,guest_launch=False),indent=2)+'\n')
print('233 corrected build002 selected; preliminary build/test retained')
