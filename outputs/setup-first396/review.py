"""Close the nonexecuted control without claiming an observed boot transition."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'control001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(K/'frozen.json')
for p,h in pins.items():assert sha(W/p)==h,p
before=read(O/'before.json');c=read(O/'collection.json');s=read(O/'final-state.json');a=read(O/'audit.json')
assert before['completed'] and c['completed'] and s['closed']
assert s['normal_startup_restored'] and s['original_driver_restored'] and s['original_F_retained']
assert a['integrity_passed'] and not a['diagnostic_workload_completed'] and not a['strict_qualification_passed']
assert a['normal_shutdown_count']==0 and not a['new_events']['system'] and not a['new_events']['application']
same={p:c['files'][p]==v for p,v in before['files'].items()};assert all(same.values())
assert all(c['files'][p] is None for p in c['files'] if p.startswith('/E/xwndemo396control001/'))
count=0
for record,root in [(before,K/'artifacts/control001-before'),(c,K/'artifacts/control001')]:
 for p,v in record['files'].items():
  if v is None:continue
  q=root/p.lstrip('/');assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256'];count+=1
for phase in ['before','after']:
 r=read(O/(phase+'-scan')/'trial.json');assert r['collected']
 for n,v in r['files'].items():
  p=Path(r['private'])/n;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'];count+=1
r=dict(closed=True,windows_execution_evidence=False,launch_accepted=True,offline_transition_observed=False,
 normal_startup_and_original_driver_restored=True,all_baseline_files_unchanged=True,integrity_scope_passed=True,
 workload_completed=False,strict_qualification_passed=False,normal_shutdown_count=0,new_system_events=0,new_application_events=0,
 frozen_inputs_verified=len(pins),private_records_rehashed=count,boot_cause='Unknown; user observation requested',
 no_rerun_or_recollect=True,observer_stopped_record='control001/observer-stop001.json',
 private_captures={p.relative_to(K).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p)) for p in (K/'artifacts').rglob('*') if p.is_file()})
p=K/'final-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print('396 closed: no Windows execution evidence;',len(pins),'pins;',count,'capture records verified')
