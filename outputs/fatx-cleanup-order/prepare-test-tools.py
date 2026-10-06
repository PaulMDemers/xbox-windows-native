"""Prepare the same bounded concurrency probe for the isolated0099 candidate."""
from pathlib import Path
import hashlib,json,shutil
k=Path(__file__).resolve().parent;control=k.parent/'fatx-shutdown-concurrency'
for name in ['Run.ps1','supervise.py','trial.py','audit.py','audit-allocation.py','capture-timeout.py','decode-timeout.py','qualify.py','read-resource-layouts.py','read-probe-symbols.py']:
    target=k/name;assert not target.exists()
    text=(control/name).read_text().replace('fatx-shutdown-concurrency','fatx-cleanup-order')
    if name=='audit.py':text=text.replace('unchanged FATX0098/video0093','candidate0099 and unchanged video0093')
    target.write_text(text)
for name in ['probe.c','probe-review.json','probe-symbols.json','kernel-resource-layouts.json']:
    assert not (k/name).exists();shutil.copyfile(control/name,k/name)
(k/'artifacts').mkdir(exist_ok=True)
shutil.copyfile(control/'artifacts/probe.exe',k/'artifacts/probe.exe')
assert hashlib.sha256((k/'artifacts/probe.exe').read_bytes()).hexdigest()==json.loads((k/'probe-review.json').read_text())['probe_sha256']
text=(control/'prepare.py').read_text().replace('fatx-shutdown-concurrency','fatx-cleanup-order')
text=text.replace("r['payloads'].append(w.write('xwnidle/concurrent.exe',helper))", """driver=(k/'artifacts/xwnfatx.sys').read_bytes()
binary=json.loads((k/'binary-review.json').read_text());assert binary['passed'] and m.sha(driver)==binary['sha256']
driver_path='winnt/system32/drivers/xwnfatx.sys'
m.replace(w,driver_path,driver)
for row in r['payloads']+r['preserved_payloads']:
    if row['path']==driver_path:row.update(sha256=m.sha(driver),bytes=len(driver))
r['fatx_sha256']=m.sha(driver)
r['payloads'].append(w.write('xwnidle/concurrent.exe',helper))""")
text=text.replace('No raw writes, lock/dismount, registry edits, UI actions or driver changes.','Only FATX driver changes to candidate0099. No raw writes, lock/dismount, registry edits or UI actions.')
text=text.replace('with unchanged drivers.','with candidate0099 and unchanged video0093.')
(k/'prepare-fixture.py').write_text(text)
print('Candidate tools prepared; driver review and fixture preparation still required')
