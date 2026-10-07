import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'crash002';run=k.parents[1]/'work/runs/nt5-controlled-dump-observe-crash002'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (run/'cleanup.json').exists() and not (out/'closure.json').exists()
names=['cleanup.json','instance.json','input-hashes.json','disk-retention.json','cpu-trace.log']
r=dict(physical_access=False,never_relaunch=True,private_disk=str(run/'hdd.qcow2'),private_disk_sha256=sha(run/'hdd.qcow2'),metadata_sha256={n:sha(run/n) for n in names})
(out/'closure.json').write_text(json.dumps(r,indent=2)+'\n');print('Closed crash002, evidence retained')
