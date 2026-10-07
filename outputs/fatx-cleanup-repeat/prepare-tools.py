"""Repeat0099 with the documented wait-all success range; retain the prior held run."""
import shutil,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'fatx-cleanup-order';control=k.parent/'fatx-shutdown-concurrency'
assert not (k/'fixture-001.json').exists() and not (k/'probe-review.json').exists()
for name in ['Run.ps1','supervise.py','trial.py','audit.py','audit-allocation.py','capture-timeout.py','decode-timeout.py','qualify.py','prepare-fixture.py']:
    p=k/name
    text=(prior/name).read_text().replace('fatx-cleanup-order','fatx-cleanup-repeat')
    if name=='audit.py':text=text.replace(r'WAIT_RESULT 0 ([0-9]+)',r'WAIT_RESULT [0-2] ([0-9]+)')
    p.write_text(text)
for name in ['Build.ps1','review.py','read-probe-symbols.py']:
    shutil.copyfile(control/name,k/name)
for name in ['binary-review.json','fatx-layouts.json','kernel-resource-layouts.json']:
    shutil.copyfile(prior/name,k/name)
(k/'artifacts').mkdir(exist_ok=True);shutil.copyfile(prior/'artifacts/xwnfatx.sys',k/'artifacts/xwnfatx.sys')
source=(control/'probe.c').read_text();old='if(status!=WAIT_OBJECT_0){report("HELD_FOR_DIAGNOSIS"';assert source.count(old)==1
(k/'probe.c').write_text(source.replace(old,'if(status>=WAIT_OBJECT_0+3){report("HELD_FOR_DIAGNOSIS"'))
r=dict(scope=__doc__,previous_probe_sha256=json.loads((control/'probe-review.json').read_text())['probe_sha256'],
       previous_run='fatx-cleanup-order001',actual_wait_all_result=2,
       api_source='https://learn.microsoft.com/en-us/windows/desktop/api/synchapi/nf-synchapi-waitformultipleobjects',
       contract='For bWaitAll TRUE, any result from WAIT_OBJECT_0 through WAIT_OBJECT_0+nCount-1 means all objects signaled.',
       correction='Accept 0,1,2 for three thread handles; still reject timeout, abandonment and failure. Require exact500/500/500 counters and zero errors in cold qualification.',
       historical_result='All1500 operations completed in16620ms, exact files, no contended FATX resources; helper intentionally held on valid result2. No normal shutdown; historical qualification remains FAIL.')
(k/'waitall-correction.json').write_text(json.dumps(r,indent=2)+'\n')
