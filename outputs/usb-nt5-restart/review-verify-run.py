"""Qualify an existing-driver boot separately from installation and UI actions."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];case='emu002';out=k/case
run=repo/('work/runs/nt5xidrestart-'+case)
read=lambda p:json.loads(p.read_text())
assert (run/'cleanup.json').exists()
r=read(k/(case+'-review.json'));d=read(out/'details.json');t=read(out/'device-state.json');s=read(run/'stage.json')
log=(run/'verify.log').read_bytes();rows=[]
try:
    decoded=log.decode('ascii')
    assert all(v in [9,10,13] or 32<=v<127 for v in log),'Non-text control bytes'
except (UnicodeDecodeError,AssertionError) as error:
    result=dict(case=case,physical_access=False,existing_driver_input_passed=False,input_evidence_unverifiable=True,
        cold_integrity_passed=False,scoped_subsequent_boot_passed=False,normal_restart_passed=False,
        strict_events_passed=d['strict_events_passed'],strict_event_note='No new decoded events is not evidence of a successful boot or shutdown.',
        log_validation_error=str(error),verify_log_sha256=hashlib.sha256(log).hexdigest(),
        installed_driver_exact=r['checks']['installed_driver_exact'],allocation_errors=r['allocation_errors'],orphan_cluster_count=r['orphan_cluster_count'],
        limits='Corrupted log prevents any HID-read conclusion. No normal shutdown/dashboard return. Physical Xbox untouched.')
    (out/'verify-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0)
for line in decoded.splitlines():
    if re.fullmatch('[0-9a-f]{26}',line):continue
    m=re.fullmatch('([A-Z_]+) ([0-9a-f]{8}) tick=([0-9]+)',line);assert m,line
    rows.append((m[1],int(m[2],16),int(m[3])))
def values(name):return [v for n,v,tick in rows if n==name]
collection_ok=not r['collection_errors'] or r['collection_errors']==["exit-verify.txt: 'exit-verify.txt'"]
integrity=(r['protected_exact'] and r['allocation_consistent'] and not r['orphan_cluster_count']
    and not r['allocation_errors'] and collection_ok
    and all(all(h[key] for key in ['header_valid','checksum_valid','sequences_equal']) for h in r['hives'].values())
    and all(h['parsed'] for h in d['hives'].values())
    and d['event_history_preserved'] and d['setupapi_history_preserved']
    and t['selected_policy_unchanged'] and t['no_new_device_disabling'])
input_ok=(values('VERIFY_EXISTING_DRIVER')==[1] and values('HID_READ_PASS')==[200]
    and values('OPEN_CYCLE')==[0,1] and values('CYCLE_PASS_REPORTS')==[100,100]
    and not any(n.startswith(('INSTALL_ONCE','INSTALL_BEGIN','KNOWN_WIZARD','HELPER_','FAIL_')) for n,v,tick in rows)
    and r['checks']['installed_driver_exact'] and s['phase']=='verify' and not s['driver_reinstalled'] and not s['wizard_actions_enabled'])
restart_ok=(values('NORMAL_RESTART_REQUEST')==[0] and values('INSTALL_WAIT_RESULT')==[0]
    and values('INSTALL_FINAL_RESULT')==[0] and len(values('SETUP_IDLE_OBSERVED_MS'))==1
    and values('SETUP_IDLE_OBSERVED_MS')[0]>=5000 and r['dashboard_returned'] and d['normal_shutdown_count']==1)
result=dict(case=case,physical_access=False,existing_driver_input_passed=bool(input_ok),cold_integrity_passed=bool(integrity),
    scoped_subsequent_boot_passed=bool(input_ok and integrity and restart_ok),normal_restart_passed=bool(restart_ok),
    strict_events_passed=d['strict_events_passed'],collection_errors_retained=r['collection_errors'],
    shell_exit_note='Post-process shell echo is optional after a guest restart; raw collector finding retained.',
    verify_log_sha256=hashlib.sha256(log).hexdigest(),driver_sha256=s['build_files']['xwnxid.sys'],
    limits='Same installed driver in a fresh child disk; no installation or wizard helper. Idle cached reads only, no deliberate controls or driver stop/removal/device-power coverage. No physical qualification.')
(out/'verify-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
