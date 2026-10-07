"""Retarget an unlaunched soak plan to0101; preserve the stress-PASS prerequisite."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;fixed=k.parent/'fatx-directory-order';ws=k.parents[1]
assert not list(k.glob('fixture-*.json')) and not (ws/'work/runs/nt5-fatx-lock-order-soak-004').exists()
assert not (k/'retarget.json').exists()
r={'scope':__doc__,'physical_access':False,'old_driver_sha256':hashlib.sha256((k/'artifacts/xwnfatx.sys').read_bytes()).hexdigest()}
for name in ['prepare-tools.py','prepare.py','README.md']:
    p=k/name;text=p.read_text().replace('fatx-namespace-order','fatx-directory-order').replace('fatx-namespace-stress','fatx-directory-order').replace('0100','0101');p.write_text(text)
for name in ['binary-review.json','fatx-layouts.json','kernel-resource-layouts.json']:
    shutil.copyfile(fixed/name,k/name)
shutil.copyfile(fixed/'artifacts/xwnfatx.sys',k/'artifacts/xwnfatx.sys')
# Decoder uses exact0101 globals; no concurrent.exe is staged in this full soak.
for name in ['capture-timeout.py','decode-timeout.py']:
    text=(fixed/name).read_text().replace('fatx-directory-order','fatx-lock-order-soak').replace("['001']","['004']")
    (k/name).write_text(text)
r['new_driver_sha256']=hashlib.sha256((k/'artifacts/xwnfatx.sys').read_bytes()).hexdigest()
r['preparation_gate']='fatx-directory-order/001/qualification.json passed'
(k/'retarget.json').write_text(json.dumps(r,indent=2)+'\n')
