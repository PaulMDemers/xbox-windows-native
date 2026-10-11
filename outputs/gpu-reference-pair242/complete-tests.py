"""Fresh host-test IDs; preserve failed helper/header/capsule setup attempts."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
for old,new,idold,idnew in [('test-inventory004.py','test-inventory005.py','test004','test005'),('test-guards.py','test-guards003.py','guard-test002','guard-test003')]:
 p=k/new;assert not p.exists();p.write_text((k/old).read_text(encoding='utf-8').replace(idold,idnew),encoding='utf-8')
p=k/'prelaunch-review.py';s=p.read_text(encoding='utf-8').replace('inventory-test004','inventory-test005').replace('guard-test002','guard-test003');p.write_text(s,encoding='utf-8')
(k/'setup-failure003.json').write_text(json.dumps(dict(stage='guard-test002',error='Missing copied primary gdb source capsule; no result published',guest_launch=False,completed_checks_not_qualified=True,next='guard-test003 with hash-pinned original241 capsule'),indent=2)+'\n',encoding='utf-8')
