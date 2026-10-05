"""Evaluate bounded hardware-test eligibility using preserved baseline history.
This does not turn a strict no-popup audit into PASS or fix the popup's cause.
"""
import hashlib,json,runpy
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
x=runpy.run_path(str(k/'assess-control.py'))
read=lambda p:json.loads(p.read_text())
history_path=ws/'outputs/native-windows-paint-save/matched-emulator-validation.json'
files_path=ws/'outputs/native-windows-paint-save/nt5-paint-matched-001-save-audit.json'
history=read(history_path);files=read(files_path);candidate=read(k/'audit.json')
old_popups=[v for v in history['new_system_records'] if v['source']=='Application Popup']
stops=[v for v in history['new_system_records'] if v['source']=='EventLog' and v['event_id']==6006]
checks={
 'historical_test_passed':history['passed'] and history['driver_changes'] is False and files['passed'],
 'historical_miniport_matches_captured_baseline':any(v['name']=='xboxvnt5.sys' and v['matches'] and v['sha256']==x['original'] for v in files['drivers']),
 'identical_historical_popup':bool(old_popups) and all(x['signature'](v)==x['expected'] for v in old_popups),
 'historical_popups_within_five_seconds_before_shutdown':bool(stops) and all(any(s['record']>v['record'] and 0<=s['generated_unix']-v['generated_unix']<=5 for s in stops) for v in old_popups),
 'history_predates_candidate_test':max(v['generated_unix'] for v in history['new_system_records'])<min(v['generated_unix'] for v in candidate['new_events']['system']),
 'candidate_other_checks':x['other_checks'](candidate,2,'two_dashboard_returns'),
 'candidate_only_exact_shutdown_popup':x['shutdown_only'](candidate),
 'compiled_driver_tests_passed':read(k/'compiled-tests.json')['passed']}
inputs=[history_path,files_path,k/'audit.json',k/'compiled-tests.json']
r={'scope':__doc__,'eligible_for_bounded_physical_trial':all(checks.values()),'checks':checks,
 'strict_candidate_audit_passed':candidate['passed'],'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs],
 'decision':'Retain the exact shutdown popup as an unresolved baseline limitation. Proceed only with a bounded reversible hardware trial; its per-cycle no-new-popup gate remains strict.',
 'limits':'Two fresh controls did not reproduce the popup. Earlier exact-baseline evidence did; this supports an intermittent pre-existing issue but does not establish its mechanism. No delayed-write, unexpected error, unknown popup, failed workload or missing shutdown is exempted.'}
(k/'historical-assessment.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
