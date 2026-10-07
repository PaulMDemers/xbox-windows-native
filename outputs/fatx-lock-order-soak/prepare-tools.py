"""Prepare the original full15-minute workload with candidate0101; gate staging on stress PASS."""
import shutil
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'shutdown-null-placeholder';fixed=k.parent/'fatx-directory-order'
for name in ['Run.ps1','supervise.py','trial.py','audit-workload.py','audit-package.py','audit-allocation.py','inventory.py']:
    p=k/name;assert not p.exists()
    p.write_text((prior/name).read_text().replace('shutdown-null-placeholder','fatx-lock-order-soak'))
for name in ['capture-timeout.py','decode-timeout.py']:
    text=(fixed/name).read_text().replace('fatx-directory-order','fatx-lock-order-soak').replace("['001']","['004']")
    (k/name).write_text(text)
for name in ['binary-review.json','fatx-layouts.json','kernel-resource-layouts.json']:
    shutil.copyfile(fixed/name,k/name)
shutil.copyfile(prior/'xwntest.inf',k/'xwntest.inf')
(k/'artifacts').mkdir(exist_ok=True);shutil.copyfile(fixed/'artifacts/xwnfatx.sys',k/'artifacts/xwnfatx.sys')
text=(prior/'prepare-workload.py').read_text()
text=text.replace("case=sys.argv[1];assert case in ['003','004']","case=sys.argv[1];assert case=='004'\nassert json.loads((k.parent/'fatx-directory-order/001/qualification.json').read_text())['passed']")
text=text.replace("(k/'fixture-001.json')","(k.parent/'shutdown-null-placeholder/fixture-001.json')")
for rel in ['002/audit.json','002/package-audit.json','003/audit.json','003/allocation.json','completed001-copy.json']:
    text=text.replace("(k/'"+rel+"')","(k.parent/'shutdown-null-placeholder/"+rel+"')")
text=text.replace("('shutdown-null-placeholder-'+case", "('fatx-lock-order-soak-'+case").replace("('work/shutdown-null-placeholder-'+case","('work/fatx-lock-order-soak-'+case")
text=text.replace('m.replace(w,startup,script);w.flush()', '''driver=(k/'artifacts/xwnfatx.sys').read_bytes()
review=json.loads((k/'binary-review.json').read_text());assert review['passed'] and m.sha(driver)==review['sha256']
driver_path='winnt/system32/drivers/xwnfatx.sys';m.replace(w,driver_path,driver)
for row in r['payloads']+r['preserved_payloads']:
    if row['path']==driver_path:row.update(sha256=m.sha(driver),bytes=len(driver))
r['fatx_sha256']=m.sha(driver)
m.replace(w,startup,script);w.flush()''')
text=text.replace("if case=='004':r['intervention']='Only startup command uses original full-duration workload without rehearsal argument; binaries and BMP unchanged, settled configuration and trace retained.'", "if case=='004':r['intervention']='FATX0101 plus original full-duration startup command; original workload binaries, BMP, video, hives and trace unchanged during staging.'")
(k/'prepare.py').write_text(text)
