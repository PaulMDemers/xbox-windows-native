"""MIT. Close physical attempt with cleanup separate from game-test success."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
st=read('stage001.json');col=read('collection001.json');run=read('load-run-review001.json')
assert st['completed'] and col['completed']
checks={n:read('supervisor001-'+n+'.json')['closed'] and read('supervisor001-'+n+'.json')['completed'] for n in ['stage','launch','collect']}
checks.update(hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'],registry_restored=read('registry-review001.json')['passed'],system_hives_clean=read('audit1.json')['hives_clean'],user_hive_clean=read('user-hive-audit001.json')['passed'],welcome_preserved=read('welcome-review001.json')['passed'],old_save_preserved=run['checks']['XWN586.SV4_preserved'],new_save_preserved=run['checks']['XWN593.SV4_preserved'])
assert all(checks.values())
for row in col['files'].values():assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
assert read('observation001.json')['dashboard_return']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cleanup_checks=checks,load_run_passed=run['passed'],load_behavior_proved=False,runner_present=run['checks']['runner_present'],normal_shutdown_proved=run['checks']['normal_shutdown'],user_observation=read('user-observation001.json')['reported'],console_at_dashboard=True,no_owned_startup_hook=True,owned_host_processes_closed=True,physical_access=True,cold_start_confirmed=False,limits='Windows startup returned early; no reload qualification. Hives/selected files checked, not full FATX allocation. No FPS/GPU claim.',pins={n:sha(K/n) for n in ['package001.json','stage001.json','launch001.json','collection001.json','audit1.json','load-run-review001.json','user-observation001.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['closed','runner_present','normal_shutdown_proved','load_run_passed']}))
