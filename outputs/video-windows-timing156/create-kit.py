"""Fresh timing kit with unchanged Windows141 guest and reviewed emulator pair."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-windows-coherence155'
assert json.loads((old/'verification.json').read_text())['ordinary_matched_pair_passed']
pins={}
for name in ['atomic_json.py','audit.py','cold-map.py','common.py','configuration.py','prepare.py',
             'preflight.py','probe.c','protocol.py','record-closure.py','verify.py','verify-series.py',
             'test-oracle.py','test-protocol.py','test-pixels.py','pixels.py','lifecycle.py','test-lifetime.py','close-series.py']:
    p=old/name;dest=k/name;assert not dest.exists();data=p.read_bytes();pins[name]=hashlib.sha256(data).hexdigest()
    if name.endswith('.py'):
        data=data.replace(b'video-windows-coherence155',b'video-windows-timing156').replace(b'nt5-vwin155-',b'nt5-vtime156-')
    dest.write_bytes(data)
(k/'artifacts').mkdir(exist_ok=False);shutil.copyfile(old/'artifacts/probe.exe',k/'artifacts/probe.exe')
shutil.copyfile(old/'pe-review.json',k/'pe-review.json')
(k/'creation.json').write_text(json.dumps(dict(parent=str(old),source_pins=pins,
    unchanged_probe_and_guest_driver=True,physical_access=False,debugger=False,
    ordinary_parent_qualification_sha256=hashlib.sha256((old/'verification.json').read_bytes()).hexdigest()),indent=2)+'\n')
print('Fresh timing sources only; no guest prepared/launched')
