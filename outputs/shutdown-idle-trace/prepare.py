"""Copy an immutable idle-install seed; never edit guest contents or reuse a run."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k.parent/'shutdown-install-idle/fixture-002.json').read_text())
base=k.parent/'native-windows-fatx-forensics/artifacts'/r['fixture_name']
seed=ws/'work/shutdown-install-idle-002-seed.qcow2';target=ws/'work/shutdown-idle-trace-001-seed.qcow2'
assert sha(base)==r['fixture_sha256'] and sha(seed)==r['seed_sha256']
assert not target.exists() and not (k/'fixture-001.json').exists()
shutil.copyfile(seed,target);assert sha(target)==r['seed_sha256']
r.update(scope='Debugger replay of the exact ordinary first-install idle failure; no guest edits.',
 source_manifest='shutdown-install-idle/fixture-002.json',case='001',debugger_observation=True)
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n')
