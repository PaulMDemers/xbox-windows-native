"""Narrow eligibility for a controlled hardware trial, not a clean emulator-boot claim."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
audit=k/'rehearsal/audit.json';a=load(audit)
control=k.parent/'fatx-mapped-eof/old/audit.json';old=load(control)
key=lambda v:(v['source'],v['event_id'],v['type'],v['strings'],v['data_hex'])
checks=dict(
    prior_physical_trial_passed=load(k.parent/'fatx0098-physical-trial/qualification.json')['passed'],
    allocation_consistent=load(k/'rehearsal/allocation-artifacts/allocation.json')['allocation_consistent'],
    api_probe_completed=a['probe_completed'] and a['mapped_checks_passed'],
    persistence_passed=a['persistence_passed'],normal_shutdown=a['normal_shutdown_count']==1,
    dashboard_return=a['dashboard_return'],payloads_exact=all(v['matched'] for v in a['payloads']),
    baseline_exact=all(a['baseline_checks'].values()) and a['fatx_exact'],
    hives_readable=all(v['parsed'] for v in a['hives']),no_unexpected_errors=not a['unexpected_errors'],
    no_application_events=not a['new_events']['application'],
    popup_matches_old_control=all(any(key(v)==key(o) for o in old['popup_records']) for v in a['popup_records']))
r=dict(scope=__doc__,checks=checks,eligible_for_controlled_trial=all(checks.values()),
       strict_emulator_run_passed=a['ordinary_run_valid'],unresolved_emulator_popups=a['popup_records'],
       audit_sha256=hashlib.sha256(audit.read_bytes()).hexdigest(),control_audit_sha256=hashlib.sha256(control.read_bytes()).hexdigest(),
       decision='Storage/API checks and normal restart pass. Preserve the known shutdown installer popup as a failed strict emulator gate; do not infer its cause or waive a physical popup. The already-authorized isolated hardware trial changes no driver and requires independent strict physical audits.',
       hardware_qualified=False)
(k/'eligibility.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));assert r['eligible_for_controlled_trial']
