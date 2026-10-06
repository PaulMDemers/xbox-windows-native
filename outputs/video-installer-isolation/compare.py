"""Compare the named ordinary intervention/control runs without promoting a driver."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
names=['audio003','control003','pair004'];fixtures={};audits={};rows={}
for name in names:
 fixtures[name]=json.loads((k/name/'fixture.json').read_text())
 audits[name]=a=json.loads((k/name/'audit.json').read_text())
 launch=json.loads((k/name/'launch.json').read_text())
 rows[name]=dict(strict_passed=a['passed'],popup_count=len(a['new_popup_records']),
   install_commands=a['new_interactive_install_commands'],config_flags_after=a['device_config_flags_after'],
   graphics_passed=all(c['pixel_and_timing_workload_passed'] for c in a['cycles']),
   direct_ram_uc_verified=a['direct_ram_uc_verified'],payloads_match=all(v['matched'] for v in a['payloads']),
   other_checks_passed=all([a['trace_valid'],all(a['baseline_checks'].values()),a['expected_device_state_retained'],
      not a['unexpected_errors'],not a['new_events']['application'],
      all(c['pixel_and_timing_workload_passed'] and c['normal_restart_requested'] for c in a['cycles']),
      a['direct_ram_uc_verified'],all(v['matched'] for v in a['payloads']),a['normal_shutdown_count']==1,a['one_dashboard_return']]),
   normal_shutdowns=a['normal_shutdown_count'],dashboard_return=a['one_dashboard_return'],
   launched_utc=launch['cycles'][0]['launch_requested_utc'])
assert fixtures[names[0]]['parent_fixture_sha256']==fixtures[names[1]]['parent_fixture_sha256']
assert fixtures[names[0]]['payloads']==fixtures[names[1]]['payloads']
assert fixtures['control003']['system_before_sha256']==fixtures['control003']['system_after_sha256']==fixtures['audio003']['system_before_sha256']
assert fixtures['audio003']['registry_edit']['only_expected_value_changed']
assert fixtures['pair004']['registry_edit']['only_expected_values_changed']
assert fixtures['pair004']['parent_fixture_sha256']==fixtures['control003']['parent_fixture_sha256']
assert fixtures['pair004']['payloads']==fixtures['control003']['payloads']
assert fixtures['pair004']['system_before_sha256']==fixtures['control003']['system_before_sha256']
assert rows['audio003']['launched_utc']<rows['control003']['launched_utc']
assert rows['control003']['launched_utc']<rows['pair004']['launched_utc']
result=dict(scope=__doc__,physical_access=False,identical_driver_and_workload_payloads=True,results=rows,
 limits='One single-device intervention, one fresh control, and one two-device follow-up after an earlier failed control. Timing is not deterministic; no statistics, ordinary baseline driver fix, audio support, physical qualification or performance improvement established.')
if not all(v['other_checks_passed'] for v in rows.values()):
 result['interpretation']='Other required checks failed; this pair cannot isolate the popup question.'
elif rows['audio003']['popup_count']==0 and rows['control003']['popup_count']>0:
 result['interpretation']='This pair supports involvement of the pending01B0 installation; it does not establish a driver correction or permanent remedy.'
elif rows['audio003']['popup_count']>0:
 result['interpretation']='Marking only01B0 failed-install did not eliminate shutdown popups. Compare any changed installer target before extending the hypothesis.'
else:
 result['interpretation']='Both runs have no popups; this pair cannot distinguish the intervention from intermittency.'
if all(v['other_checks_passed'] for v in rows.values()) and [rows[n]['popup_count'] for n in ['control003','audio003','pair004']]==[2,1,0]:
 result['interpretation']='Popup counts track the selected pending-install state: control2, audio-only1, two-device0. This supports a queued device-install/shutdown interaction; it does not qualify a video driver or implement the missing devices.'
elif all(v['other_checks_passed'] for v in rows.values()) and rows['control003']['popup_count']==0:
 result['interpretation']='The unchanged control was clean, confirming intermittency. The intervention changed which installer ran, but these runs do not establish a popup fix or prove the pending queue caused every failure.'
(k/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
