"""Actual acceptance predicates with read-only real inputs and modeled record mutations."""
import copy,json
from pathlib import Path
import gates
K=Path(__file__).resolve().parent;real_read=gates.read
cases=['success','wrong_identity','unverified_payload','copy_failure','missing_shutdown','new_application_event','different_warning','strict_claim','missing_restore','changed_original_hash','correction_broadened']
results=[]
for scenario in cases:
 def read(p):
  r=copy.deepcopy(real_read(p));s=Path(p).as_posix()
  if s.endswith('/candidate001/corrected-analysis002.json'):
   a=r['corrected_audit']
   if scenario=='wrong_identity':r['correct_expected_identity']='0'*64
   if scenario=='unverified_payload':r['candidate_payload_equals_frozen_build']=False
   if scenario=='copy_failure':a['cmd_persistence_passed']=False
   if scenario=='missing_shutdown':a['normal_shutdown_count']=0
   if scenario=='new_application_event':a['new_events']['application']=[{'event_id':1}]
   if scenario=='different_warning':a['warnings_errors'][0]['event_id']=50
   if scenario=='strict_claim':a['strict_qualification_passed']=True
   if scenario=='changed_original_hash':r['original_records_unchanged']['audit.py']='0'*64
   if scenario=='correction_broadened':r['changed_audit_fields']['integrity_passed']={'original':False,'corrected':True}
  if s.endswith('/candidate001/final-state.json') and scenario=='missing_restore':r['original_driver_restored']=False
  return r
 gates.read=read;failed=False
 try:gates.validation()
 except AssertionError:failed=True
 assert failed==(scenario!='success'),scenario
 results.append(dict(case=scenario,refused=failed))
gates.read=real_read
p=K/'gate-host001.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,cases=results,scope='Actual gate predicates; record mutations modeled; original files unchanged; no hardware access'),indent=2)+'\n')
print('Actual gate accepted pinned scope and rejected ten modeled invalid results')
