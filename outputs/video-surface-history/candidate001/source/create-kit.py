"""Create a new lifecycle diagnostic from closed callback evidence; no launch."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-surface-callback'
names=['atomic_json.py','audit.py','cold-map.py','common.py','configuration.py','discover_kernel.py','Invoke-Exclusive.ps1','preflight.py','prepare.py','probe.c','protocol.py','record-closure.py','Run.ps1','check-leases.ps1','supervise.py','test-oracle.py','test-protocol.py','verify.py','trace.py','verify-trace.py','test-verifier.py','sites.json','pe-review.json','runner-review.json','toolchain.json','surface_trace.py','verify-surface.py','test-surface.py','test-recorded-surface.py','backend.py']
pins={}
for n in names:
 p=old/n;dest=k/n;assert not dest.exists();data=p.read_bytes();pins[n]=hashlib.sha256(data).hexdigest()
 if n.endswith(('.py','.ps1')):data=data.replace(b'video-surface-callback',b'video-surface-history').replace(b'nt5-vsurface-',b'nt5-vlife-')
 dest.write_bytes(data)
(k/'artifacts').mkdir(exist_ok=False);shutil.copyfile(old/'artifacts/probe.exe',k/'artifacts/probe.exe')
(k/'creation.json').write_text(json.dumps(dict(parent=str(old),source_pins=pins,probe_reused_unchanged=True,driver_changed=False,emulator_changed=False,physical_access=False),indent=2)+'\n')
print('Created unique host kit only')
