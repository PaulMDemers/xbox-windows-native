"""Reuse the reviewed corrected five-worker workload; change only candidate0101."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'fatx-namespace-stress'
for name in ['Run.ps1','supervise.py','trial.py','audit.py','audit-allocation.py','capture-timeout.py','decode-timeout.py','qualify.py','prepare-fixture.py']:
    target=k/name;assert not target.exists()
    text=(prior/name).read_text().replace('fatx-namespace-stress','fatx-directory-order').replace('candidate0100','candidate0101')
    if name=='Run.ps1':
        text=text.replace("throw 'Unlaunched0100 fixture held: cleanup-repeat proved parent-directory cache-flush inversion. Use reviewed0101 kit.'\n",'')
    target.write_text(text)
for name in ['probe.c','probe-review.json','probe-symbols.json','kernel-resource-layouts.json','waitall-correction.json']:
    assert not (k/name).exists();shutil.copyfile(prior/name,k/name)
(k/'artifacts').mkdir(exist_ok=True)
shutil.copyfile(prior/'artifacts/probe.exe',k/'artifacts/probe.exe')
assert hashlib.sha256((k/'artifacts/probe.exe').read_bytes()).hexdigest()==json.loads((k/'probe-review.json').read_text())['probe_sha256']
for name in ['review-binary.py','prepare-layouts.py']:
    target=k/name;assert not target.exists()
    target.write_text((k.parent/'fatx-namespace-order'/name).read_text().replace('fatx-namespace-order','fatx-directory-order').replace('0100','0101'))
print('Tools prepared; await fresh driver build, review and offset compilation before fixture staging')
