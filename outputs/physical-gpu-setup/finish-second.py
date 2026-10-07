"""Finalize bounded second-boot GPU evidence without waiving warnings or prior log corruption."""
import json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'002';sys.path.insert(0,str(k.parent/'fatx0101-physical'));import physical as m
trial=json.loads((case/'physical.json').read_text());assert trial.get('collected_utc');audit=json.loads((case/'binary-audit.json').read_text());assert audit['complete']
allocation=json.loads((case/'allocation.json').read_text());events=json.loads((case/'events-and-log-review.json').read_text());state=json.loads((case/'setup-state-review.json').read_text());prior=json.loads((k/'first-setup-review.json').read_text())
record=case/'final-state.json';assert not record.exists()
with m.connect() as f:
 m.owner(f);checks=m.checks(f,True);assert m.passed(checks)
 assert m.sha(m.get(f,m.startup))==trial['before']['startup.cmd']['sha256']
 assert m.get(f,'/F/xwninf102/software.bak')==(k/'artifacts/before-software').read_bytes()
 assert m.get(f,'/F/winnt/inf/oem2.inf')==(k/'artifacts/xwnvideo.inf').read_bytes()
 for name in ['system','software','setupapi.log']:
  row=trial['after'][name];assert m.sha(m.get(f,row['path']))==row['sha256']
 final=dict(utc=m.utc(),checks=checks,normal_startup_unchanged=True,software_backup_exact=True,installed_oem_inf_exact=True,collected_system_software_setupapi_unchanged=True,dashboard_available=True,no_new_windows_launch=True)
 m.save(final,record)
gpu_persisted=state['gpu']==prior['gpu'] and state['service']==prior['service'] and len(state['gpu'])==1 and state['gpu'][0]['values'].get('ConfigFlags')==0
integrity=bool(audit['passed'] and audit['checked']==audit['expected_count']==3439 and len(audit['hives'])==9 and all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in audit['hives']) and allocation['capture_complete'] and allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count'])
gates=dict(gpu_registration_persisted=gpu_persisted,no_repeated_gpu_installer=not events['setupapi_new_gpu_install'],normal_shutdown=events['normal_shutdown_event'],no_new_log_anomaly=events['setupapi_exact_prior_prefix'] and events['setupapi_new_non_ascii_bytes']==0,cold_integrity=integrity,strict_events=events['strict_event_gate'],prior_log_anomaly_resolved=False,unattended_setup_proven=False)
r=dict(scope=__doc__,evidence_class='physical, user-assisted setup',configuration_verified=gpu_persisted and integrity and events['normal_shutdown_event'],strict_qualification_passed=all(gates.values()),gates=gates,remaining=['Identify and handle01B0/01B4/01C1/USBffff:ffff without generic suppression','Resolve intended raw-C shadow-image capacity integration; Srv2013 still fails strict event gate','Investigate first-boot111-byte malformed log prefix; no clean-shutdown record for that boot','Validate unattended setup/normal reboot before another strict long soak'],limits='No graphics acceleration/mode change or new driver binary; no recovery capture/release promotion. Setup wizard cancellation was manual. Historic malformed log preserved.')
m.save(r,case/'qualification.json');print(json.dumps(r,indent=2))
