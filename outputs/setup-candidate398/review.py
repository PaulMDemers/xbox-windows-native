"""Verify closure, frozen inputs and captures independently of test verdict."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'candidate001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(K/'frozen.json')
for p,h in pins.items():assert sha(W/p)==h,p
b=read(O/'before.json');c=read(O/'collection.json');s=read(O/'final-state.json');a=read(O/'audit.json');t=read(O/'candidate-analysis.json')
assert b['completed'] and c['completed'] and s['closed']
assert s['normal_startup_restored'] and s['original_driver_restored'] and s['original_F_retained']
assert c['tested_fatx_sha256']==read(K/'package.json')['candidate']['sha256']
count=0
for record,root in [(b,K/'artifacts/candidate001-before'),(c,K/'artifacts/candidate001')]:
 for p,v in record['files'].items():
  if v is None:continue
  q=root/p.lstrip('/');assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256'];count+=1
for phase in ['before','after']:
 r=read(O/(phase+'-scan')/'trial.json');assert r['collected']
 for n,v in r['files'].items():
  p=Path(r['private'])/n;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'];count+=1
assert not (K.parent/'demo-bundle395/accepted-state.json').exists()
r=dict(closed=True,tested_driver='candidate390',normal_startup_and_original0101_restored=True,
 original_F_retained=True,console_C_accessed=False,frozen_inputs_verified=len(pins),private_records_rehashed=count,
 setup_before_files_passed=t['setup_before_files_passed'],candidate_file_scope_passed=t['candidate_file_scope_passed'],
 integrity_scope_passed=a['integrity_passed'],scoped_combined_passed=t['scoped_combined_passed'],
 strict_qualification_passed=t['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],
 no_adoption_or_bundle=True,no_rerun_or_recollect=True,
 private_captures={p.relative_to(K).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (K/'artifacts').rglob('*') if p.is_file()})
p=K/'final-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:v for n,v in r.items() if n!='private_captures'},indent=2))
