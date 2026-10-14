"""Explicit scoped demo acceptance; strict/release failures remain failures."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];T=K.parent/'setup-candidate398'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CANDIDATE='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'
def validation():
 for path,h in read(K/'frozen.json').items():assert sha(W/path)==h,path
 for path,h in read(T/'frozen.json').items():assert sha(W/path)==h,path
 correction=read(T/'candidate001/corrected-analysis002.json');review=read(T/'final-review002.json')
 assert sha(T/'candidate001/corrected-analysis002.json')==review['analysis_sha256']
 assert sha(T/'corrected-analysis002.py')==review['analysis_source_sha256']
 for path,h in correction['original_records_unchanged'].items():assert sha(T/path)==h,path
 assert correction['correct_expected_identity']==CANDIDATE and correction['candidate_payload_equals_frozen_build']
 assert correction['negative_identity_cases_rejected']==5
 assert correction['changed_audit_fields']=={n:{'original':False,'corrected':True} for n in ['tested_fatx_verified','scoped_combined_passed','diagnostic_workload_completed']}
 a=correction['corrected_audit'];c=read(T/'candidate001/collection.json');f=read(T/'candidate001/final-state.json')
 assert all(a[n] for n in ['diagnostic_workload_completed','scoped_combined_passed','cmd_persistence_passed','file_persistence_passed','tested_fatx_verified','integrity_passed','mode720p_passed'])
 assert a['normal_shutdown_count']==1 and not a['new_events']['application']
 assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
 assert not a['strict_qualification_passed'] and not a['release_qualified']
 assert f['closed'] and f['normal_startup_restored'] and f['original_driver_restored'] and f['original_F_retained']
 assert c['completed'] and c['driver_restored'] and c['tested_fatx_verified']
 assert sha(T/'artifacts/candidate001/tested-fatx.sys')==c['tested_fatx_sha256']==CANDIDATE
 assert sha(Path(read(T/'package.json')['candidate']['source']))==CANDIDATE
 assert not (K.parent/'demo-bundle395/accepted-state.json').exists()
 return a
