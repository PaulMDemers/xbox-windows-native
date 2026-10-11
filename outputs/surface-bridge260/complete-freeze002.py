"""Finish missing002 manifest after successful review; preserve wrong parent lookup."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'emulator-frozen002.json').exists()
r=read(k/'runtime-review002.json');assert r['passed'] and r['source_sha256']==sha(k/'review-runtime002.py')
assert "surface-pattern258/emulator-frozen002.json" in (k/'review-runtime002.py').read_text()
record=dict(passed=True,prior_failure='review-runtime002 completed checks then looked for nonexistent parent surface-pattern258/emulator-frozen002.json',
 prior_review_preserved=True,parent_actual='outputs/surface-pattern258/emulator-frozen.json',guest_launched=False,
 source_sha256=sha(Path(__file__)))
(k/'freeze002-recovery.json').write_text(json.dumps(record,indent=2)+'\n')
frozen=read(k.parent/'surface-pattern258/emulator-frozen.json')
for p in k.glob('*'):
 if p.is_file() and p.suffix in ('.py','.c','.h','.ps1','.json','.patch') and p.name!='emulator-frozen002.json':frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu002/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu002/fixture.json')
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():frozen[n]=h
(k/'emulator-frozen002.json').write_text(json.dumps(frozen,indent=2)+'\n');print('Fresh002 frozen manifest completed;',len(frozen),'inputs; no guest launched')
