"""Verify closed physical evidence and original restoration; never touches console."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=K/'final-review.json';assert not dest.exists();pair=read(K/'pair-results.json')
r=dict(evidence_complete=False,performance_qualified=False,release_qualified=False,cases={},source_sha256=sha(Path(__file__)))
pins=read(K/'frozen.json')
for n,h in pins.items():assert sha(W/n)==h,n
for n,h in read(K/'postflight-tools.json')['source_sha256'].items():assert sha(K/n)==h,n
for case in ['control001','candidate001']:
    out=K/case;final=read(out/'final-state.json');assert final['closed'] and final['normal_startup_restored'] and final['original_driver_restored'] and final['original_F_retained']
    assert sha(out/'audit.json')==final['audit_sha256']
    total=0
    for folder,receipt in [(case+'-before',out/'before.json'),(case,out/'collection.json')]:
        for n,v in read(receipt)['files'].items():
            if v is not None:assert sha(K/'artifacts'/folder/n.lstrip('/'))==v['sha256'],n;total+=1
    for phase in ['before','after']:
        scan=read(out/(phase+'-scan')/'trial.json');assert scan['collected']
        for n,v in scan['files'].items():assert sha(Path(scan['private'])/n)==v['sha256']
    trial=read(out/'trial.json');assert trial['launch_requested'] and not trial['startup_enabled'] and trial['driver_restored']
    assert sha(K/'artifacts'/case/'tested-driver.dll')==trial['test_driver_sha256']
    r['cases'][case]=dict(captured_files_rehashed=total,final_state_sha256=sha(out/'final-state.json'),audit_sha256=sha(out/'audit.json'),driver_sha256=trial['test_driver_sha256'],restored_original_sha256=trial['original_driver_sha256'],closed=True)
r.update(evidence_complete=True,frozen_inputs=len(pins),pair_sha256=sha(K/'pair-results.json'),diagnostic_pair_completed=pair['diagnostic_pair_completed'],scoped_combined_passed=pair['scoped_combined_passed'],strict_qualification_passed=pair['strict_qualification_passed'],limits='Fresh E/F protected/hive checks plus complete E allocation and declared capture hashes. No C tool access, full-disk content proof, audibility observation, event waiver or performance promotion.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed evidence and baseline restoration verified; strict result',r['strict_qualification_passed'])
