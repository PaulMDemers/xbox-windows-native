"""Summarize completed physical audits while retaining strict event failures."""
import json
from physical import k,save,utc
q=json.loads((k/'qualification.json').read_text())
s=json.loads((k/'installed-state.json').read_text())
a=json.loads((k/'allocation.json').read_text())
b=json.loads((k/'binary-audit.json').read_text())
assert not q['allocation_audit_pending'] and not q['binary_audit_pending'] and b['complete']
w=q['workload']
r=dict(scope=__doc__,recorded_utc=utc(),physical_result=True,
       workload_passed=w['passed'],mapping_checks=w['mapping_checks'],
       timed_rounds=len(w['timed_rounds']),last_elapsed_ms=w['timed_rounds'][-1][1],
       final_files_exact=sum(v['matched'] for v in w['files']),
       deleted_intermediates_absent=sum(w['deleted_files_absent'].values()),
       paint_api_replay_passed=w['paint_api_replay_passed'],
       normal_shutdown=q['normal_shutdown'],unexpected_events=q['unexpected_errors'],
       shutdown_popups=q['popups'],new_application_events=q['new_events']['application'],
       allocation=a,binary_hashes_checked=b['checked'],binary_audit_passed=b['passed'],
       structural_hives_checked=len(b['hives']),installed_state_passed=s['passed'],
       strict_qualification_passed=q['passed'],recovery_capture_performed=False,
       actual_paint_ui_observations='No new manual application observations for this attempt; earlier user files preserved separately.',
       timing_limit='Observer stopped without a return marker. Exact dashboard return time and host process termination cause are unknown; user later confirmed dashboard.',
       next_step='Diagnose recurrent shutdown installer popup and Srv warnings before another strict qualification; preserve current driver/video baseline.')
r['classification']='Full timed workload and cold integrity passed; strict qualification failed on event gates' if w['passed'] and a['allocation_consistent'] and b['passed'] and s['passed'] and not q['passed'] else 'Inspect detailed qualification'
save(r,k/'summary.json');print(r['classification'])
