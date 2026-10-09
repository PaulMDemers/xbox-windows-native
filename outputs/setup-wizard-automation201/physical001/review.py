"""Independent raw physical lifecycle, active-dialog context and preserved-byte review; no FTP."""
import hashlib, json
from pathlib import Path
from analyze import analyze
k=Path(__file__).resolve().parent;ws=k.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'review.json';assert not dest.exists()
r=read(k/'physical.json');a=read(k/'audit.json');closed=read(k/'closure.json')
assert closed['closed'] and closed['scoped_cancellation_passed'] and a['scoped_cancellation_passed']
for name,digest in closed['pins'].items():assert sha(k/name)==digest,name
for name,digest in read(k/'ready.json')['pins'].items():assert sha(ws/name)==digest,name
for phase in ['before','after']:
    for row in r[phase].values():assert row is not None and sha(ws/row['path'])==row['sha256']
wizard=(ws/r['after']['wizard201.log']['path']).read_bytes()
guardian=(ws/r['after']['guardian201.log']['path']).read_bytes()
parsed=analyze(wizard,guardian)
assert parsed['cancellation_lifecycle_passed'] and parsed['targets']==[1,2,3,4]
assert parsed['actions']==4 and len(parsed['owners'])==4 and len(parsed['closed'])==4
rows=[(line.split()[0],list(map(int,line.split()[1:]))) for line in wizard.decode('ascii').splitlines()]
foreground=[v for label,v in rows if label=='FG_BEFORE']
active=[v for label,v in rows if label=='GUI_BEFORE_ACTIVE']
captures=[v for label,v in rows if label=='GUI_BEFORE_CAPTURE']
verified=[v for label,v in rows if label=='CANCEL_ACTIVE_VERIFIED']
assert len(foreground)==len(active)==len(captures)==len(verified)==4
assert all(fg[:2]==intent[:2] and gui[1]==intent[1] and cap==[0,0,0] and check[:2]==intent[:2]
           for fg,gui,cap,check,intent in zip(foreground,active,captures,verified,parsed['intents']))
assert a['integrity_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
assert not r['startup_enabled'] and r['startup_restored_verified'] and r['helpers_exact'] and r['rollback_exact']
assert len(a['hives'])==10 and all(v['parsed'] and v['header_valid'] for v in a['hives'])
assert a['typed_state']['no_new_device_disabling'] and a['typed_state']['selected_policy_unchanged']
assert not a['typed_state']['device_binding_delta']
assert not a['strict_events_passed'] and not a['physical_qualified'] and not a['release_qualified']
assert len(a['warnings_errors'])==1 and a['warnings_errors'][0]['source']=='Ftdisk' and a['warnings_errors'][0]['event_id']==49
result=dict(passed=True,physical_access=False,physical_result_review=True,scoped_lifecycle_passed=True,
            four_physical_targets=parsed['targets'],unique_owner_lifetimes=parsed['owners'],
            raw_foreground=foreground,raw_active=active,raw_capture=captures,
            strict_events_passed=False,physical_qualified=False,release_qualified=False,
            evidence_pins={name:sha(k/name) for name in ['physical.json','return.json','audit.json','device-state.json','closure.json','ready.json']},
            source_sha256=sha(Path(__file__)),
            limits='Unattended known-dialog cancellation/normal restart only; no driver support, benchmark, full allocation/file-content audit or release promotion. Ft49 preserved strict failure.003 observer stale suffix unresolved.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Physical201 raw lifecycle/active context/ten hives/protected/startup review passed; sole Ft49 remains strict FALSE')
