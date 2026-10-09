"""Both fresh ordinary202 lifecycles required before physical permission; no event waiver."""
from common import *
dest=k/'emulator-pair-review.json';assert not dest.exists()
cases=[]
for case in ['control001','candidate001']:
    out=k/('emu-'+case);a=read(out/'audit.json');c=read(out/'closure.json')
    assert c['closed'] and c['audit_sha256']==sha(out/'audit.json')
    assert a['scoped_display_passed'] and a['integrity_passed'] and not a['debugger'] and not a['physical_access']
    assert a['boundary_analysis']['helper']['targets']==[1,2,5]
    assert all(v['moves']==40 and v['exact_readbacks']==40 for v in a['window_samples'])
    assert len(a['warnings_errors'])==1 and [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
    assert not a['strict_qualification_passed'] and a['normal_shutdown_count']==1
    cases.append(dict(case=case,audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),scoped_display_passed=True,strict_events_passed=False))
assert read(k/'emu-control001/audit.json')['actual_caps']==read(k/'emu-candidate001/audit.json')['actual_caps']
assert read(k.parent/'setup-wizard-automation201/physical001/review.json')['passed']
save(dest,dict(passed=True,physical_access=False,cases=cases,strict_events_passed=False,
 limits='Fresh ordinary joined-helper benchmark scope, inheritedFt49 remains strict failure. Not physical speed or release qualification.'))
print('Fresh202 matched emulator scopes and explicit warning limits reviewed')
