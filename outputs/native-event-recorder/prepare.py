"""Prepare identical immutable seeds for recorder-disabled and recorder-enabled runs."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((k.parent/'shutdown-install-idle/fixture-002.json').read_text())
seed=ws/'work/shutdown-install-idle-002-seed.qcow2'
assert sha(seed)==f['seed_sha256']
for case,role in [('001','recorder_disabled'),('002','recorder_enabled')]:
    dest=ws/('work/native-event-recorder-'+case+'-seed.qcow2')
    manifest=k/('fixture-'+case+'.json')
    assert not dest.exists() and not manifest.exists()
    shutil.copyfile(seed,dest);assert sha(dest)==f['seed_sha256']
    row=dict(f,case=case,role=role,source_manifest='shutdown-install-idle/fixture-002.json',
             scope='Identical first-install idle fixture; only host recorder enablement differs.')
    manifest.write_text(json.dumps(row,indent=2)+'\n')
