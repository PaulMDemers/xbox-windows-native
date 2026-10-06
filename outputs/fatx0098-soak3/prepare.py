"""Prepare a fresh physical attempt using byte-identical rehearsed helpers."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'fatx0098-soak2'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not (k/'physical.json').exists()
sources=['physical.py','workload.py','watch.py','scan.py','qualify.py','audit-binaries.py','audit-manual.py','final-state.py','verify-installed.py','capture-recovery.py','test-verifier.py']
evidence=['probe-review.json','matched-review.json','fixture-rehearsal.json','eligibility.json','rehearsal/audit.json']
rows=[]
for name in sources+evidence+['artifacts/probe.exe','artifacts/matched.exe','artifacts/scribble.bmp']:
    source=old/name;target=k/name;data=source.read_bytes()
    if name in ['scan.py','watch.py']:data=data.replace(b'XWNSoak98b',b'XWNSoak98c')
    if name=='capture-recovery.py':data=data.replace(b"'/F/xwns98-first']",b"'/F/xwns98-first','/F/xwns98-second']")
    target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists(),str(target)
    target.write_bytes(data);rows.append(dict(path=name,source_sha256=sha(source.read_bytes()),sha256=sha(data)))
(k/'derivation.json').write_text(json.dumps(dict(previous_attempt='outputs/fatx0098-soak2',scope='Fresh attempt; previous reports and binaries reused only as provenance, not new validation. Same probe path requires verified archival rename before staging.',files=rows),indent=2)+'\n')
