"""Close one accepted physical attempt with no guest result; never retry it."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final001.json';assert not out.exists()
st=read('stage001.json');launch=read('launch001.json');col=read('collection001.json');audit=read('audit1.json')
assert st['completed'] and launch['requested'] and col['completed'] and col['hook_removed']
assert not col.get('result_directory') and '/E/xwn582/runner.txt' not in col['files']
assert audit['changed_files']==[] and audit['hives_clean']
assert audit['events']['system']['normal_shutdown_delta']==0
assert not audit['events']['system']['new_records'] and not audit['events']['application']['new_records']
assert read('registry-review001.json')['passed'] and read('welcome-review001.json')['passed'] and read('user-hive-audit001.json')['passed']
for action in ['stage','launch','collect']:
    s=read('supervisor001-'+action+'.json');assert s['closed'] and s['completed'] and not s['deadline_reached']
assert set(col['game_rows'])=={n for n in st['staged'] if n.startswith('/E/xwn582-kit/game/')}
unchanged={n:row['unchanged'] for n,row in col['files'].items() if n.startswith('/E/xwn582-kit/game/')}
assert all(unchanged.values())
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       physical_attempt=583,allowed_launches=1,accepted_launches=1,retries=0,
       result='No guest result after accepted ordinary launch; dashboard return only',
       guest_runner_observed=False,windows_desktop_observed=False,screen_observation='unwatched',
       input_qualified=False,normal_shutdown_proved=False,new_eventlog6006=0,
       hook_removed=True,console_state='dashboard reachable at completed collection',
       ordinary_launcher_startup_720p_preserved=True,baseline_files_changed=[],
       system_hives_clean=True,user_hive_clean=True,game_registry_unchanged=True,
       welcome_preferences_unchanged=True,game_inventory_files=len(col['game_rows']),
       selected_game_files_unchanged=unchanged,all_owned_host_processes_closed=True,
       temporary_hook_outstanding=False,physical_access=True,console_C_accessed=False,
       root_cause='Unresolved; no screen or early-boot trace. Consistent with prior launch intermittency, not proof of that cause.',
       next='Do not repeat this attempt or keep retrying unchanged boots. Preserve583 and use a fresh watched/cold-start attempt when the user can reset. Continue independent host preparation.',
       limits='No new Xbox game, scrolling, fullscreen, Welcome-close, save, FPS or GPU evidence. Selected cold files and inventory are not a whole FATX allocation audit.',
       pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and p.suffix in ['.py','.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print('Physical583 CLOSED without guest result; hook removed, baseline unchanged')
