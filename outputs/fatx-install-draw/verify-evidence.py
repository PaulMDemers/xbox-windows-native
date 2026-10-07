"""Verify recorded outcomes, source preservation, and staged evidence bytes."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
review=read(k/'probe-review.json');ui=read(k/'ui-preservation.json');pair=read(k/'comparison.json')
for name,key in [('probe.c','source_sha256'),('Build.ps1','build_script_sha256')]:assert sha((k/name).read_bytes())==review[key]
original=(k.parent/'fatx-install-alignment/probe.c').read_bytes();combined=(k/'probe.c').read_bytes()
assert sha(original)==ui['original_source_sha256'] and sha(combined)==ui['combined_source_sha256']
old_prefix=original.replace(b'\r\n',b'\n').split(b'void WINAPI mainCRTStartup(void) {')[0]
new_prefix=combined.replace(b'\r\n',b'\n').split(b'static HANDLE Ready,Stop,DrawLog;')[0]
assert old_prefix==new_prefix and sha(old_prefix)==ui['matcher_and_action_prefix_sha256']
for case in ['001','002']:
 q=read(k/case/'qualification.json');assert q['ui_assisted_diagnostic'] and not q['physical_qualified'] and not q['ordinary_stability_qualified']
 assert q['passed']==all(q['gates'].values())
 assert sha((k/case/'qualification.json').read_bytes())==pair['qualification_sha256'][case]
 for name,digest in q['evidence_sha256'].items():assert sha((k/case/name).read_bytes())==digest
 for stage in read(k/case/'collection.json')['stages'].values():assert sha((k/case/stage['output']).read_bytes())==stage['sha256']
 assert next(p for p in read(k/case/'audit.json')['payloads'] if p['path']=='xwnidle/probe.exe')['sha256']==review['probe_sha256']
checked=[]
for rel in subprocess.check_output(['git','ls-files','--',k.relative_to(ws).as_posix()],cwd=ws,text=True).splitlines():
 p=ws/rel;assert subprocess.check_output(['git','show',':'+rel],cwd=ws)==p.read_bytes(),p
 checked.append(rel)
assert checked and not pair['physical_qualified'] and not pair['ordinary_stability_qualified']
assert pair['passed']==all(v['passed'] for v in pair['cases'])
print(json.dumps(dict(evidence_verified=True,recorded_pair_passed=pair['passed'],staged_files_checked=len(checked),ui_prefix_preserved=True,physical_qualified=False)))
