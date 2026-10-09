"""Independent raw-log/binding review of two closed unattended emulator lifecycles."""
import hashlib, importlib, json, sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'completed-review.json';assert not dest.exists()
analyze=importlib.import_module('analyze-cancel002').analyze
results=[]
for case in ['cancel006','cancel007']:
    out=k/case;art=out/'artifacts';a=read(out/'audit.json');closed=read(out/'closure.json')
    assert closed['closed'] and closed['diagnostic_usable']
    assert closed['audit_sha256']==sha(out/'audit.json')
    assert a['diagnostic_usable'] and a['integrity_passed'] and a['normal_shutdown_count']==1
    raw=analyze((art/'wizard201.log').read_bytes(),(art/'guardian201.log').read_bytes())
    assert raw==read(out/'cancellation.json') and raw['cancellation_lifecycle_passed']
    assert raw['targets']==[1,2,5] and len(raw['closed'])==3 and not raw['failures']
    launch=read(out/'launch.json');assert len(launch['cycles'])==1
    assert launch['cycles'][0]['offline_observed'] and launch['cycles'][0]['dashboard_return']
    allocation=read(out/'allocation.json')
    assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
    assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives'])
    assert all(v['matched'] for v in a['files']) and a['typed_state']['no_new_device_disabling']
    assert not a['strict_events_passed'] and not a['ordinary_qualified'] and not a['physical_qualified']
    assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
    for name,digest in read(k/('frozen-'+case+'.json')).items():assert sha(ws/name)==digest,name
    fixture=read(k/('fixture-'+case+'.json'))
    assert fixture['files']['F/xwnwiz201/wizard.exe']==read(k/'build-review006.json')['binary_sha256']
    results.append(dict(case=case,scoped_lifecycle_passed=True,strict_events_passed=False,
                        ordinary_qualified=False,physical_qualified=False,raw_targets=raw['targets'],
                        evidence={name:sha(out/name) for name in ['audit.json','closure.json','cancellation.json','launch.json','allocation.json']}))
assert (k/'guardian-physical001.c').read_text()==(k/'guardian002.c').read_text().replace('/cancel-emulator','/cancel-physical')
result=dict(passed=True,cases=results,physical_access=False,
            limits='Build-review write_scope mentions parent BN_CLICKED: actual pinned006 source sends BM_CLICK to the actual Cancel BUTTON. Original prelaunch metadata retained; no implication its return value means success. Actual closures/idle/restart/return are the evidence. Original003 stale observer tail unresolved.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Independent raw lifecycle/binary/frozen-input review passed for006/007; strict Ft49 failures retained')
