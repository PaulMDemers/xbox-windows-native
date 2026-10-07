"""Verify the closed ordinary comparison without waiving any strict event gate."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fixtures=[read(k/('fixture-'+c+'.json')) for c in ['control001','candidate001']]
audits=[read(k/c/'audit.json') for c in ['control001','candidate001']]
for case,f,a in zip(['control001','candidate001'],fixtures,audits):
    assert (k/case/'closure.json').exists() and not a['debugger'] and not a['explicit_ui_intervention']
    assert f['mode']==0 and f['readback_verified'] and f['result_absent']
    assert a['strict_qualification_passed']==(a['workload_and_persistence_passed'] and a['integrity_passed'] and a['strict_events_passed'])
    pre=read(k/case/'preflight.json')
    for n,d in pre['sources'].items():assert sha(k/case/'source'/n)==d
for key in ['parents','preserved_hives','payloads','startup_sha256','parent_manifest_sha256','build_review_sha256']:
    assert fixtures[0][key]==fixtures[1][key],key
diff=[]
for before,after in zip(fixtures[0]['protected'],fixtures[1]['protected']):
    assert (before['volume'],before['path'])==(after['volume'],after['path'])
    if before['sha256']!=after['sha256']:diff.append(before['volume']+'/'+before['path'])
assert diff==['E/Applications/XWNFBoot/loader/halxboxnt5.dll']
assert read(k/'inputs.json')['profiles']==read(k/'control-inputs.json')['profiles']
assert read(k/'counter-tests.json')['passed']
r=dict(scope=__doc__,changed_protected_files=diff,same_helper_and_initial_hives=True,same_build_flags=True,physical_access=False,actual_crash_dump_write_qualified=False,
    results=[dict(case=case,workload=a['workload_and_persistence_passed'],integrity=a['integrity_passed'],strict=a['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],events=[dict(source=e['source'],id=e['event_id'],data=e['data_hex']) for e in a['warnings_errors']]) for case,a in zip(['control001','candidate001'],audits)])
target=k/'pair-review.json'
if target.exists():assert read(target)==r
else:target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
