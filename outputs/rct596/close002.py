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
checks.update(hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'],registry_restored=read('registry-review002.json')['passed'],system_hives_clean=read('audit1.json')['hives_clean'],user_hive_clean=read('user-hive-audit001.json')['passed'],welcome_preserved=read('welcome-review001.json')['passed'],old_save_preserved=run['checks']['XWN586.SV4_preserved'],new_save_preserved=run['checks']['XWN593.SV4_preserved'])
checks['cleanup_host_closed']=read('supervisor-cleanup001-cleanup.json')['closed'] and read('supervisor-cleanup001-cleanup.json')['completed']
checks['cleanup_cold_readback']=read('cleanup-apply001.json')['completed']
assert all(checks.values())
for row in col['files'].values():assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
assert read('observation001.json')['dashboard_return']
visual=read('visual-review001.json') if (K/'visual-review001.json').exists() else {}
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cleanup_checks=checks,load_run_passed=run['passed'],exact_saved593_reload_visually_proved=visual.get('passed',False),user_confirmed_manual_save_load=read('user-observation001.json')['manual_save_load_works'],runner_present=run['checks']['runner_present'],normal_shutdown_proved=run['checks']['normal_shutdown'],user_observation=read('user-observation001.json')['reported'],console_at_dashboard=True,no_owned_startup_hook=True,owned_host_processes_closed=True,physical_access=True,cold_start_confirmed=read('hardware-ready001.json')['user_confirmed_off_10_seconds_and_dashboard'],limits='One cold-start physical watched Load attempt. Load qualification requires separate user/visual evidence. Hives/selected files checked, not full FATX allocation. No FPS/GPU claim.',pins={n:sha(K/n) for n in ['package001.json','stage001.json','launch001.json','collection001.json','audit1.json','load-run-review001.json','user-observation001.json','cleanup-preparation002.json','cleanup-apply001.json','registry-review002.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['closed','runner_present','normal_shutdown_proved','load_run_passed']}))
