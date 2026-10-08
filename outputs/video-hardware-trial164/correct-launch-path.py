"""Preserve prelaunch path guard failure; new reviewed launcher, no original edit."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];original=k/'Run.ps1';fixed=k/'Run-Helper.ps1'
assert not fixed.exists() and not (k/'candidate001/runner-start.json').exists()
text=original.read_text(encoding='utf-8');assert text.count('video-physical-hardware-trial164')==1
text=text.replace('video-physical-hardware-trial164','video-hardware-trial164').replace('frozen-inputs.json','helper-frozen-inputs.json')
fixed.write_text(text,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(k/'launch-path-failure.json').write_text(json.dumps(dict(error='Copied launcher expected nonexistent video-physical-hardware-trial164 seed instead of prepared video-hardware-trial164 seed',
    failed_source_sha256=sha(original),corrected_source_sha256=sha(fixed),bootstrap_started=False,windows_launch_requested=False,
    original_frozen_source_unchanged=True,correction='New launcher changes only seed path and extends immutable source manifest'),indent=2)+'\n',encoding='utf-8')
pins=json.loads((k/'frozen-inputs.json').read_text(encoding='utf-8'))
for name,digest in pins.items():assert sha(ws/name)==digest,name
for p in [fixed,k/'correct-launch-path.py',k/'launch-path-failure.json',k/'frozen-inputs.json']:
    pins[str(p.relative_to(ws)).replace('\\','/')]=sha(p)
(k/'helper-frozen-inputs.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
out=k/'candidate001/helper-launch-source';out.mkdir(exist_ok=False)
for p in [fixed,k/'correct-launch-path.py',k/'launch-path-failure.json',k/'helper-frozen-inputs.json']:shutil.copyfile(p,out/p.name)
