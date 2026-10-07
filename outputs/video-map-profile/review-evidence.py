"""Read-only final evidence/source review; does not run or collect a guest."""
import ast,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sources=0;closed=[]
for kit,case in [('video-copy-profile-visible','baseline002'),('video-map-profile','control001'),('video-map-profile','candidate001')]:
 out=k.parent/kit/case;pre=read(out/'preflight.json');a=read(out/'audit.json');c=read(out/'closure.json')
 for n,h in pre['sources'].items():assert sha(out/'source'/n)==h;sources+=1
 assert sha(Path(c['private_disk']))==c['private_disk_sha256']
 assert a['strict_qualification_passed'] and not a['debugger'] and not a['explicit_ui_intervention']
 assert all(v['elapsed_ms']>=300 or v['count']==4096 for v in a['protocol_details']['cases'])
 assert a['protocol_details']['verified_pixel_stages']==162
 closed.append(dict(kit=kit,case=case,audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json')))
failure=read(k.parent/'video-copy-profile/baseline001/audit.json')
assert not failure['strict_qualification_passed'] and not failure['protocol_exact']
assert read(k.parent/'video-copy-profile-visible/baseline001/host-failure.json')
pair=read(k/'pair-review.json');assert pair['passed'] and pair['postprocessor_sha256']==sha(k/'summarize-pair.py')
for case,pins in pair['evidence'].items():
 for name,h in pins.items():assert sha(k/case/name)==h
parsed=[]
for kit in ['video-copy-profile','video-copy-profile-visible','video-map-profile']:
 for p in (k.parent/kit).rglob('*.py'):ast.parse(p.read_text());parsed.append(str(p.relative_to(ws)))
r=dict(passed=True,physical_access=False,guest_operation=False,source_sha256=sha(Path(__file__)),frozen_source_pins=sources,closed=closed,failed_attempts_retained=True,python_syntax_files=len(parsed),pair_sha256=sha(k/'pair-review.json'),limits='Source/evidence integrity check; does not replace guest pixel checks or cold audits. No new hardware or scanout qualification.')
p=k/'review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
