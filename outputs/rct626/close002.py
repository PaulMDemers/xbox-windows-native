"""Close recording626 using collected evidence and separate user observations."""
import datetime, hashlib, json, struct
from pathlib import Path
K = Path(__file__).resolve().parent
read = lambda name: json.loads((K / name).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = K / 'final001.json'
assert not out.exists()
b, c, a = read('before001.json'), read('collection001.json'), read('audit1.json')
assert b['completed'] and c['completed'] and a['hives_clean']
assert read('registry-review001.json')['game_registry_subtree_restored']
assert read('user-hive-review001.json')['passed']
assert not c['temporary_hook_installed'] and c['remote_writes'] == []
for action in ('snapshot', 'launch', 'collect'):
    s = read('supervisor001-' + action + '.json')
    assert s['closed'] and s['completed'] and not s['deadline_reached']
for group in (b, c):
    for row in group['files'].values():
        p = Path(row['path'])
        assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
runner = Path(c['files']['/E/xwn624/runner.txt']['path']).read_text()
pairs = [line.split('=', 1) for line in runner.splitlines()]
assert len({p[0] for p in pairs}) == len(pairs)
values = {key: int(value) for key, value in pairs}
for key, value in dict(schema=624, wait=0, game_exit=0, launched=1, registry_restored=1,
                       parent_disposition=1, key_disposition=1).items():
    assert values[key] == value, key
backup = Path(c['files']['/E/xwn624/registry.bin']['path']).read_bytes()
assert len(backup) == 1572
headers = [struct.unpack_from('<III', backup, offset) for offset in (0, 524, 1048)]
# Type output is not meaningful when the queried value does not exist.
assert all(exists == 0 and size == 0 for exists, value_type, size in headers)
saves = [n for n in c['files'] if '/Saved Games/' in n]
assert saves and all(n in b['files'] and b['files'][n]['sha256'] == c['files'][n]['sha256'] for n in saves)
allowed = {'/E/winnt/system32/config/' + n for n in ('system','software','sam','security','default','sysevent.evt')}
allowed.add('/E/documents and settings/Win2K/NTUSER.DAT')
assert set(a['changed_files']) <= allowed
assert a['events']['system']['normal_shutdown_delta'] == 1
assert not a['events']['application']['new_records']
errors = [r for r in a['events']['system']['new_records'] if r['type'] == 1]
assert [(r['source'], r['event_id']) for r in errors] == [('Ftdisk', 49)]
u = read('user-observation001.json')
assert u['game_ran_reported'] and u['right_mouse_scrolling_reported'] and u['arrow_key_scrolling_reported']
assert read('user-observation002.json')['console_state'] == 'UnleashX dashboard'
r = dict(closed=True, recording_session_passed=True, cleanup_passed=True,
         utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), launch_count=1,
         user_reported_game_and_scrolling=True, runner=values, backup_headers=headers,
         launcher_interval_ms=(values['end_tick']-values['start_tick']) & 0xffffffff,
         selected_files_collected=len(c['files']), saved_game_directory_files_unchanged=len(saves),
         normal_shutdown_delta=1, system_and_user_hives_clean=True,
         game_registry_subtree_restored=True, temporary_hook_installed=False,
         processes_closed=True, console_state='UnleashX dashboard',
         retained_limitations=['Ftdisk49', 'No full FATX allocation audit',
           'No game FPS or native GPU acceleration qualification',
           'Recording completion not reported', 'Fullscreen and sound deferred'],
         pins={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ('closed','recording_session_passed','cleanup_passed','launcher_interval_ms')}))
