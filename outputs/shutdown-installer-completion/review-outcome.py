"""Review observed setup action separately from generic cold diagnostic checks."""
import json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['001','002','003','004'];out=k/case
r=json.loads((out/'audit.json').read_text());log=r['window_observer_log']
posts=re.findall(r'GPU_FINISH_ONCE dialog=([0-9a-f]+) button=([0-9a-f]+) posted=([01])',log)
deferred=re.findall(r'GPU_RESTART_DEFER_ONCE .*?posted=([01])',log)
cancelled=re.findall(r'PLACEHOLDER_CANCEL_ONCE .*?posted=([01])',log)
samples=[]
for block in re.split(r'(?m)^SAMPLE ',log)[1:]:
    header=block.splitlines()[0];pending=re.search(r'PENDING_INSTALL status=([0-9a-f]+)',block)
    visible=[line for line in block.splitlines() if line.startswith('TOP ') and ' visible=1 ' in line]
    samples.append(dict(header=header,pending_install_status=pending[1] if pending else None,visible_top_windows=visible,gpu_success_text_present='Xbox NV2A firmware framebuffer (experimental)' in block,action_posted='GPU_FINISH_ONCE' in block,budget_exhausted='budget_exhausted=1' in block))
report=dict(case=case,physical_access=False,post_count=len(posts),posts=posts,samples=samples,
  deferred_reboot_posts=deferred,placeholder_cancel_posts=cancelled,
  restart_blocked='RESTART_BLOCKED_PENDING_INSTALL' in r['log'],
  intended_action_posted=len(posts)==1 and posts[0][2]=='1',
  final_install_queue_idle=bool(samples) and samples[-1]['pending_install_status']=='00000000',
  final_gpu_wizard_absent=bool(samples) and not samples[-1]['gpu_success_text_present'],
  cold_diagnostic_checks_passed=r['diagnostic_checks_passed'],
  dashboard_return=r['dashboard_return'],popup_records=r['popup_records'],
  ordinary_run_valid=False,hardware_qualified=False,
  limitation='Posting a notification is not proof of completion. A clean return without the action cannot establish efficacy. This helper still uses a fixed restart deadline and is not a safe production pending-install guard.')
report['targeted_setup_checks_passed']=all([report['intended_action_posted'],report['final_install_queue_idle'],report['final_gpu_wizard_absent'],report['cold_diagnostic_checks_passed'],len(samples)==5,not any(s['budget_exhausted'] for s in samples)])
if case in ['003','004']:
 report['targeted_setup_checks_passed']=report['targeted_setup_checks_passed'] and deferred==['1']
 report['limitation']='Guarded UI setup diagnostic. Pending setup prevents restart; no physical or ordinary workload qualification. Acknowledging the unsupported emulator placeholder is not implementing its driver.'
if case=='004':report['targeted_setup_checks_passed']=report['targeted_setup_checks_passed'] and cancelled==['1']
target=out/'outcome-review.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
