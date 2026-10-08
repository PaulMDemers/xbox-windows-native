"""Create a fresh diagnostic kit; no fixture, emulator or guest launch."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-upload-address2'
names=['atomic_json.py','audit.py','cold-map.py','common.py','configuration.py','discover_kernel.py','Invoke-Exclusive.ps1','preflight.py','prepare.py','probe.c','protocol.py','record-closure.py','Run.ps1','check-leases.ps1','supervise.py','test-oracle.py','test-protocol.py','verify.py','trace.py','verify-trace.py','test-verifier.py','sites.json','pe-review.json','runner-review.json','toolchain.json']
pins={}
for n in names:
 p=old/n;dest=k/n;assert not dest.exists();data=p.read_bytes();pins[n]=hashlib.sha256(data).hexdigest()
 if n.endswith(('.py','.ps1')):data=data.replace(b'video-upload-address2',b'video-surface-callback').replace(b'nt5-vaddress2-',b'nt5-vsurface-')
 dest.write_bytes(data)
(k/'artifacts').mkdir(exist_ok=False)
shutil.copyfile(old/'artifacts/probe.exe',k/'artifacts/probe.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'runner-review.json').read_text());review['local_sha256']=sha(k/'Invoke-Exclusive.ps1');(k/'runner-review.json').write_text(json.dumps(review,indent=2)+'\n')
(k/'creation.json').write_text(json.dumps(dict(parent=str(old),source_pins=pins,probe_reused_unchanged=True,driver_changed=False,physical_access=False),indent=2)+'\n')
print('Fresh host kit only; no fixture or launch')
