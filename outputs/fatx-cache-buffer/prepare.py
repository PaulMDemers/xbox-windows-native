"""Make an untouched fresh run seed from the completed control's immutable input."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((k.parent/'fatx-install-draw/fixture-001.json').read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert sha(base)==f['fixture_sha256']
seed=ws/('work/fatx-cache-buffer-'+case+'-seed.qcow2')
assert not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+base.name,str(seed)],check=True)
f.update(case=case,scope=__doc__,seed_sha256=sha(seed),source_manifest='fatx-install-draw/fixture-001.json',debugger_observation=True,physical_qualified=False)
(k/('fixture-'+case+'.json')).write_text(json.dumps(f,indent=2)+'\n')
print('Untouched control input reused with a fresh private run seed')
