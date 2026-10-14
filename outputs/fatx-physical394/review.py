"""Verify closed failed physical394 and its immutable/private evidence."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'candidate001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=read(K/'frozen.json')
for p,h in frozen.items():assert sha(W/p)==h,p
count=0
for record,root in [('before.json',K/'artifacts/candidate001-before'),('collection.json',K/'artifacts/candidate001')]:
 r=read(O/record);assert r['completed']
 for p,v in r['files'].items():
  if v is None:continue
  q=root/p.lstrip('/');assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256'],p;count+=1
for phase in ['before','after']:
 r=read(O/(phase+'-scan')/'trial.json');assert r['collected']
 for n,v in r['files'].items():
  p=Path(r['private'])/n;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'];count+=1
a=read(O/'audit.json');s=read(O/'final-state.json');c=read(O/'collection.json')
assert s['closed'] and s['normal_startup_restored'] and s['original_driver_restored']
assert c['tested_fatx_verified'] and c['protected_files_unchanged'] and all(c['original_F_and_loader_unchanged'].values())
assert a['integrity_passed'] and not a['scoped_combined_passed'] and not a['strict_qualification_passed'] and a['normal_shutdown_count']==0
assert not (K.parent/'demo-bundle395/accepted-state.json').exists()
r=dict(closed=True,physical_candidate_qualified=False,scoped_combined_passed=False,strict_qualification_passed=False,
 integrity_scope_passed=True,normal_shutdown_count=0,normal_startup_and_original_driver_restored=True,
 original_F_unchanged=True,console_C_accessed=False,frozen_inputs_verified=len(frozen),private_records_rehashed=count,
 source_review='No post-launch changes to62 frozen inputs. Candidate held after unfinished CMD second copy. Setup-first control is a separate kit; no historical requalification.',
 private_captures={p.relative_to(K).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (K/'artifacts').rglob('*') if p.is_file()},
 after_scan_scope='Complete E allocation metadata only; not full disk-content verification',
 adoption_and_bundle_held=True)
p=K/'final-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print('394 closed FAIL preserved;',len(frozen),'pins and',count,'private records verified; original driver restored')
