"""Close one physical attempt from collected evidence, including incomplete results."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
st=read('stage001.json');launch=read('launch001.json');col=read('collection001.json');audit=read('audit1.json');obs=read('observation001.json')
assert st['completed'] and launch['requested'] and col['completed'] and col['hook_removed']
assert obs['completed'] and obs['dashboard_return']
for action in ['stage','launch','collect']:
 s=read('supervisor001-'+action+'.json');assert s['closed'] and s['completed'] and not s['deadline_reached']
reg=read('registry-review001.json');welcome=read('welcome-review001.json');user=read('user-hive-audit001.json')
runner='/E/xwn589/runner.txt' in col['files']
review=read('review002.json') if runner else {}
visual=read('visual-review001.json') if (K/'visual-review001.json').exists() else {}
observation=read('user-observation001.json') if (K/'user-observation001.json').exists() else None
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_attempt=590,
 launch_requests=1,retries=0,launch_reply=launch.get('reply'),reply_uncertain=launch.get('reply_uncertain'),
 guest_runner_observed=runner,normal_shutdown_proved=audit['events']['system']['normal_shutdown_delta']==1,
 new_eventlog6006=audit['events']['system']['normal_shutdown_delta'],system_hives_clean=audit['hives_clean'],
 user_hive_clean=user['passed'],game_registry_restored=reg['passed'],welcome_preferences_preserved=welcome['passed'],
 cleanup_qualified=review.get('cleanup_qualified',False),submission_contract_passed=review.get('submission_contract_passed',False),
 captured_controls_qualified=bool(review.get('submission_contract_passed') and visual.get('passed')),
 windowed_controls_qualified=visual.get('windowed_qualified',False),fullscreen_controls_qualified=visual.get('fullscreen_qualified',False),
 user_observation=observation,hook_removed=True,temporary_hook_outstanding=False,
 console_state='dashboard reachable at completed collection',ordinary_launcher_startup_720p_preserved=col['protected_code_exact'],
 changed_baseline_files=audit['changed_files'],all_owned_host_processes_closed=True,console_C_accessed=False,
 limits='One physical attempt. Captured game output and user screen observations are distinct. No RCT save persistence, frame-rate, sound, native GPU, general filesystem-health or boot-reliability qualification.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and p.suffix in ['.py','.json']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['closed','guest_runner_observed','normal_shutdown_proved','cleanup_qualified','submission_contract_passed','captured_controls_qualified']}))
