"""MIT. Close one physical save observation without inferring reload or acceleration."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final001.json';assert not out.exists()
q=read('package002.json');st=read('stage002.json');col=read('collection001.json')
assert st['completed'] and col['completed'] and col['hook_removed']
checks={k:read(n)['completed'] and read(n)['closed'] and not read(n)['deadline_reached'] for k,n in [('stage_host_closed','supervisor002-stage.json'),('launch_host_closed','supervisor002-launch.json'),('collect_host_closed','supervisor002-collect.json')]}
a=read('audit1.json');reg=read('registry-review001.json');u=read('user-hive-audit001.json');w=read('welcome-review001.json')
checks.update(hives_clean=a['hives_clean'] and u['passed'],registry_restored=reg['passed'],welcome_preserved=w['passed'],hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'])
save=read('save-phase1-review001.json');visual=read('visual-review001.json')
prior='/E/xwn593-kit/game/Saved Games/XWN586.SV4'
checks['prior_save_preserved']=sha(col['files'][prior]['path'])==q['prior_save_preserved']==col['files'][prior]['sha256']
assert all(checks.values())
for row in col['files'].values():assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
observed=read('observation001.json');assert observed['dashboard_return']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase1_save_passed=save['passed'] and visual['passed'],cleanup_checks=checks,runner_output_present=bool(save['checks']['runner_present']),new_save_present=bool(save['checks']['new_save']),normal_shutdown_proved=a['events']['system']['normal_shutdown_delta']==1,game_registry_restored=True,physical_access=True,console_at_dashboard=True,no_owned_startup_hook=True,owned_host_processes_closed=True,reload_tested=False,cold_start_confirmed=False,save=save['save'],limits='One physical save phase. Only a later Load can prove restored game state. No full FATX allocation audit, game FPS, GPU or other-console qualification.',pins={n:sha(K/n) for n in ['package002.json','stage002.json','launch001.json','collection001.json','audit1.json','save-phase1-review001.json','visual-review001.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['closed','phase1_save_passed','runner_output_present','new_save_present','normal_shutdown_proved']}))
