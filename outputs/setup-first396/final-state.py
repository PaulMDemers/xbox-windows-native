"""Read-only post-scan restoration check; never boots or writes the console."""
import sys
from physical import K,read,connect,fetch,sha,utc,write_json,fixed,HIVES,START,DLL,FATX,pins
case=sys.argv[1];assert case in ['control001','candidate001'];out=K/case;dest=out/'final-state.json';assert not dest.exists();pins()
c=read(out/'collection.json');a=read(out/'audit.json');scan=read(out/'after-scan/trial.json');assert c['completed'] and c['startup_restored'] and c['driver_restored'] and scan['collected']
paths=list(fixed)+['/E/winnt/system32/config/'+n for n in HIVES]
paths+=list(c['original_F_and_loader_unchanged'])
r=dict(closed=False,physical_writes=False,console_C_accessed=False,files={},started_utc=utc())
with connect() as f:
    for p in dict.fromkeys(paths):
        b=fetch(f,p);assert sha(b)==c['files'][p]['sha256'],p;r['files'][p]=dict(bytes=len(b),sha256=sha(b))
    assert r['files'][FATX]['sha256']==read(out/'trial.json')['original_fatx_sha256']
    assert r['files'][DLL]['sha256']==read(out/'trial.json')['original_driver_sha256']
r.update(closed=True,dashboard_available=True,normal_startup_restored=True,original_driver_restored=True,original_F_retained=True,closed_utc=utc(),audit_sha256=sha((out/'audit.json').read_bytes()),diagnostic_workload_completed=a['diagnostic_workload_completed'],scoped_combined_passed=a['scoped_combined_passed'],strict_qualification_passed=a['strict_qualification_passed'])
write_json(dest,r);print('Post-scan baseline and rollback verified; closed',case,flush=True)
