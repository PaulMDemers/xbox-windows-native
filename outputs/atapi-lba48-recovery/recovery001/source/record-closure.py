"""Pin closed run identity and private disk; never operate the guest."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['recovery001']
out=k/case;run=ws/('work/runs/nt5-atapi-lba48-recovery-'+case)
assert (run/'cleanup.json').exists() and not (out/'closure.json').exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
paths=['cleanup.json','instance.json','input-hashes.json','disk-retention.json']
r=dict(case=case,cleanup=json.loads((run/'cleanup.json').read_text()),instance=json.loads((run/'instance.json').read_text()),physical_access=False,never_relaunch=True,private_disk=str(run/'hdd.qcow2'),private_disk_sha256=sha(run/'hdd.qcow2'),run_metadata_sha256={n:sha(run/n) for n in paths})
(out/'closure.json').write_text(json.dumps(r,indent=2)+'\n');print('Closed and pinned '+case)
