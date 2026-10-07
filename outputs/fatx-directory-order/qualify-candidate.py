"""Require independent stress replays and the original full soak before a controlled hardware trial."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={};evidence={}
for label,folder in [('stress001',k/'001'),('stress002',k/'002'),('full_soak',k.parent/'fatx-lock-order-soak/004')]:
    p=folder/'qualification.json';r=json.loads(p.read_text())
    assert r['passed'],label+' did not qualify'
    for filename,digest in r['evidence_sha256'].items():
        assert sha(folder/filename)==digest,filename
    checks[label]=True;evidence[str(p.relative_to(k.parent))]=sha(p)
review=json.loads((k/'binary-review.json').read_text());assert review['passed']
driver=k/'artifacts/xwnfatx.sys';assert sha(driver)==review['sha256']
for parent,case in [(k,'001'),(k,'002'),(k.parent/'fatx-lock-order-soak','004')]:
    assert json.loads((parent/('fixture-'+case+'.json')).read_text())['fatx_sha256']==review['sha256']
r=dict(scope=__doc__,eligible_for_controlled_hardware_trial=True,checks=checks,
       source_tree=review['source_tree'],driver_sha256=review['sha256'],evidence_sha256=evidence,
       physical_qualified=False,release_qualified=False,
       physical_baseline='FATX0098/video0093; original0088 and immutable0.1.0 preserved',
       remaining='Confirm Xromwell keyboard readiness; refresh installed hashes and preserve rollback before any deployment. Physical PnP popup and Srv2013 warnings remain strict failures, not waived by emulator results.')
p=k/'candidate-eligibility.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
