"""Verify397 closure and private evidence without replacing its verdict."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'control001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(K/'frozen.json')
for p,h in pins.items():assert sha(W/p)==h,p
before=read(O/'before.json');c=read(O/'collection.json');s=read(O/'final-state.json');a=read(O/'audit.json');control=read(O/'control-analysis.json')
assert before['completed'] and c['completed'] and s['closed']
assert s['normal_startup_restored'] and s['original_driver_restored'] and s['original_F_retained']
count=0
for record,root in [(before,K/'artifacts/control001-before'),(c,K/'artifacts/control001')]:
 for p,v in record['files'].items():
  if v is None:continue
  q=root/p.lstrip('/');assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256'];count+=1
for phase in ['before','after']:
 r=read(O/(phase+'-scan')/'trial.json');assert r['collected']
 for n,v in r['files'].items():
  p=Path(r['private'])/n;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'];count+=1
assert not (K.parent/'demo-bundle395/accepted-state.json').exists()
r=dict(closed=True,driver='original0101',normal_startup_and_original_driver_restored=True,
 original_F_retained=True,console_C_accessed=False,frozen_inputs_verified=len(pins),private_records_rehashed=count,
 setup_before_files_passed=control['setup_before_files_passed'],native_copy_discriminator_passed=control['native_copy_discriminator_passed'],
 original_duplicate_enumeration_reproduced=control['original_duplicate_enumeration_reproduced'],
 integrity_scope_passed=a['integrity_passed'],diagnostic_workload_completed=a['diagnostic_workload_completed'],
 scoped_combined_passed=a['scoped_combined_passed'],strict_qualification_passed=a['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],
 new_system_events=len(a['new_events']['system']),new_application_events=len(a['new_events']['application']),
 no_candidate_adoption_or_bundle=True,no_rerun_or_recollect=True,
 private_captures={p.relative_to(K).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (K/'artifacts').rglob('*') if p.is_file()})
p=K/'final-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:v for n,v in r.items() if n!='private_captures'},indent=2))
