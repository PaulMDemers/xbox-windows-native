import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(K/'frozen.json')
for n,h in pins.items():assert sha(W/n)==h,n
case='candidate001';out=K/case;final=read(out/'final-state.json');a=read(out/'audit.json')
assert final['closed'] and final['normal_startup_restored'] and final['original_driver_restored'] and final['original_F_retained']
assert sha(out/'audit.json')==final['audit_sha256'];total=0
for folder,receipt in [(case+'-before',out/'before.json'),(case,out/'collection.json')]:
 for n,v in read(receipt)['files'].items():
  if v is not None:assert sha(K/'artifacts'/folder/n.lstrip('/'))==v['sha256'];total+=1
for phase in ['before','after']:
 scan=read(out/(phase+'-scan')/'trial.json');assert scan['collected']
 for n,v in scan['files'].items():assert sha(Path(scan['private'])/n)==v['sha256']
trial=read(out/'trial.json');assert trial['launch_requested'] and not trial['startup_enabled'] and trial['driver_restored']
assert sha(K/'artifacts'/case/'tested-driver.dll')==trial['test_driver_sha256']
r=dict(evidence_complete=True,closed=True,captured_files_rehashed=total,frozen_inputs=len(pins),
 final_state_sha256=sha(out/'final-state.json'),audit_sha256=sha(out/'audit.json'),restored_original_sha256=trial['original_driver_sha256'],
 diagnostic_workload_completed=a['diagnostic_workload_completed'],scoped_combined_passed=a['scoped_combined_passed'],strict_qualification_passed=a['strict_qualification_passed'],
 memory_state_passed=a['memory_state_passed'],bandwidth_passed=a['bandwidth_passed'],bandwidth_samples=a['bandwidth_samples'],memory_states=a['memory_states'],performance_qualified=False,release_qualified=False,
 limits='Current physical memory-state samples and declared E/F integrity; no cache changes, full alias/TLB proof, C tool access, event waiver, or new audibility observation.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('356 closed; memory',r['memory_state_passed'],'strict',r['strict_qualification_passed'])
