"""Fresh ordinary Windows pair from pinned141 sources; no guest launch."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-surface-history'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
names=['atomic_json.py','audit.py','cold-map.py','common.py','configuration.py',
       'prepare.py','probe.c','protocol.py','record-closure.py','verify.py',
       'test-oracle.py','test-protocol.py','lifecycle.py']
pins={}
for n in names:
    p=old/n;dest=k/n;assert not dest.exists();data=p.read_bytes();pins[n]=sha(p)
    if n.endswith('.py'):
        data=data.replace(b'video-surface-history',b'video-windows-coherence155').replace(b'nt5-vlife-',b'nt5-vwin155-')
        data=data.replace(b"['candidate001']",b"['control001','candidate001']")
    if n=='prepare.py':
        data=data.replace(b"driver=k.parent/('video-clip-upload/candidate001/artifacts/xwnown.dll' if case=='candidate001' else 'video-line-upload/candidate001/artifacts/xwnown.dll')",b"driver=k.parent/'video-clip-upload/candidate001/artifacts/xwnown.dll'")
    if n=='audit.py':
        data=data.replace(b'Closed diagnostic cold audit',b'Closed ordinary cold audit')
        data=data.replace(b'debugger=True',b'debugger=False')
        data=data.replace(b'Debugger pauses exclude every timing from qualification.',b'Correctness pair; timing is not qualified by this audit.')
    if n=='verify.py':
        data=data.replace(b'ordinary_qualified=False,debugger=True',b'ordinary_qualified=bool(passed),debugger=False')
        data=data.replace(b'Debugger diagnostic; no timing qualification even if clock gates pass',b'Correctness protocol; no comparative timing qualification')
    dest.write_bytes(data)
(k/'artifacts').mkdir(exist_ok=False);shutil.copyfile(old/'artifacts/probe.exe',k/'artifacts/probe.exe')
review=read(old/'pe-review.json');assert review['passed']
review.update(control_display_sha256=review['display_sha256'],probe_reused_from='video-surface-history',
              reviewed_parent_sha256=sha(old/'pe-review.json'),same_guest_payload_both_cases=True)
(k/'pe-review.json').write_text(json.dumps(review,indent=2)+'\n')
(k/'creation.json').write_text(json.dumps(dict(parent=str(old),source_pins=pins,
    probe_reused_unchanged=True,same_driver_both_cases=True,driver_changed=False,
    physical_access=False,debugger=False),indent=2)+'\n')
print('Created fresh Windows host kit; no guest prepared or launched')
