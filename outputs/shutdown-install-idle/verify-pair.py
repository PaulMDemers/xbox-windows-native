"""Verify paired experiment evidence; preserve either run's failures."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=load(k/'probe-review.json');assert r['passed'] and r['checksum_valid']
assert sha(k/'probe.c')==r['source_sha256'] and sha(k/'Build.ps1')==r['build_script_sha256']
a,b=[load(k/('fixture-'+c+'.json')) for c in ['001','002']]
for path in ['winnt/system32/config/system','winnt/system32/xwn-video-trace.bin']:
 assert a['preserved_during_idle_staging'][path]==b['preserved_during_idle_staging'][path]
assert b['inherited_software_edit']['only_expected_value_changed']
assert a['preserved_during_idle_staging']['winnt/system32/config/software']==b['inherited_software_before_sha256']
assert b['preserved_during_idle_staging']['winnt/system32/config/software']==b['inherited_software_after_sha256']
ap={v['path']:v['sha256'] for v in a['payloads']}
bp={v['path']:v['sha256'] for v in b['payloads']}
assert all(bp[p]==digest for p,digest in ap.items())
assert set(bp)-set(ap)=={'xwninf99/xwnvideo.inf','xwninf99/xboxvnt5.sys'}
for f in [a,b]:
 assert f['idle_ms']==120000 and not f['storage_workload'] and not f['physical_access']
 assert next(v['sha256'] for v in f['payloads'] if v['path']=='xwnidle/probe.exe')==r['probe_sha256']
rows=[]
for case in ['001','002']:
 audit=load(k/case/'audit.json');package=load(k/case/'package-audit.json');launch=load(k/case/'launch.json')
 allocation=load(k/case/'allocation.json');capture=load(k/case/'allocation-capture.json')
 assert len(launch['cycles'])==1 and launch['host']=='127.0.0.1' and not launch['physical_access']
 assert capture['read_only'] and capture['nbd_process_closed'] and not capture['physical_access']
 assert len(audit['hives'])==5 and all(v['parsed'] for v in audit['hives'])
 assert package['combined_checks_passed']==(package['installation_checks_passed'] and audit['ordinary_run_valid'])
 rows.append(dict(case=case,role='control' if case=='001' else 'package',
  idle_completed=audit['idle_completed'],idle_elapsed_ms=audit['idle_elapsed_ms'],
  storage_workload_not_run=audit['storage_workload_not_run'],
  normal_shutdowns=audit['normal_shutdown_count'],popups=audit['popup_records'],
  dashboard_return=audit['dashboard_return'],ordinary_run_valid=audit['ordinary_run_valid'],
  installation_checks_passed=package['installation_checks_passed'],allocation_consistent=allocation['allocation_consistent']))
out=dict(scope=__doc__,evidence_consistent=True,physical_access=False,hardware_qualified=False,cases=rows,
 limits='Two bounded idle tests, not proof of installer process exit or popup causality. Earlier failed experiments and physical strict failures remain.')
(k/'pair-review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
