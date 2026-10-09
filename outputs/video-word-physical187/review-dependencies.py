"""Verify controller FTP/ownership dependencies match committed HEAD; no console access."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'dependency-review.json';assert not dest.exists()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ws).decode().strip();rows=[]
paths=['outputs/fatx0098-soak3/physical.py','outputs/release-0.1.0/release.json',
    'outputs/native-windows-physical-f/physical-cache-preflight.json',
    'outputs/fatx0101-physical/installed-state.json','outputs/native-windows-physical-f/decode-legacy-events.py']
for name in paths:
    current=(ws/name).read_bytes();committed=subprocess.check_output(['git','show',head+':'+name],cwd=ws)
    assert current==committed,name
    rows.append(dict(path=name,sha256=hashlib.sha256(current).hexdigest(),matches_committed_head=True))
result=dict(passed=True,physical_access=False,head=head,dependencies=rows,
    timing='Supplementary review while control001 runs; verifies unchanged committed dependencies, not a retroactive launch snapshot.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('FTP ownership/event dependencies exactly match committed HEAD; no console access')
