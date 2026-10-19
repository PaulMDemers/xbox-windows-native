"""Close the inconclusive physical scrolling attempt; preserve failures."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
col=read('collection001.json');review=read('review002.json');audit=read('audit1.json');caps=read('capture-review002.json')
assert col['completed'] and col['hook_removed'] and review['cleanup_qualified']
assert not review['submission_contract_passed'] and len(caps['captures'])==3 and not caps['comparisons']
assert review['capture_rows']==[['title','0','1','0'],['scenarios','1','1','0'],['objective','2','1','0']]
runner=Path(col['files']['/E/xwn575/runner.txt']['path']);text=runner.read_text()
assert 'target_occluded=1\ninput_sequence_submitted=0' in text
assert read('observation001.json')['completed'] and read('observation001.json')['dashboard_return']
for name in ['supervisor001-stage.json','supervisor002-stage.json','supervisor002-launch.json','supervisor002-collect.json']:assert read(name)['closed']
for name in ['stage002.json','supervisor002-stage.json','supervisor002-launch.json','supervisor002-collect.json']:assert read(name)['completed']
visual={tag:dict(path=row['path'],sha256=row['sha256']) for tag,row in caps['captures'].items()}
events=[dict(record=r['record'],source=r['source'],event_id=r['event_id']) for r in audit['events']['system']['new_records']]
changed={n:row['sha256'] for n,row in col['files'].items() if n.startswith('/E/xwn575-kit/game/') and row.get('unchanged') is False}
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=True,one_launch_only=True,launch_accepted_utc=read('launch001.json')['utc'],captured_game_title_scenarios_and_park=True,physical_display_watched=False,input_comparison_qualified=False,window_scrolling_tested=False,fullscreen_tested=False,observation='All three native GDI images show the Getting Started with Windows 2000 window over the right side of the game. Forest Frontiers renders; the overlay covers the intended objective-close click. The target-occlusion guard aborts before pause/options/scrolling cases. Blocking process identity was not logged and remains a next-probe question.',captures=visual,cleanup_qualified=True,normal_restart=True,game_exit=0,no_forced_termination=True,hives_clean=audit['hives_clean'],game_registry_restored=True,owned_hook_removed=True,all_owned_host_processes_closed=True,console_state='dashboard; no outstanding owned hook or launch',protected720p=True,ordinary_launcher_unchanged=True,console_C_accessed=False,new_system_events=events,new_application_events=audit['events']['application']['new_records'],changed_selected_game_files=changed,collection_scope=col['collection_scope'],preserved_failures=['stage001 APPE reply timeout; independent exact-prefix readback and new stage002 recovery','package001 invalid codec before outputs/access','review001 CRLF capture parser mismatch; corrected new review002; original retained','initial inline review-fix preparation rejected by PowerShell before writing sources'],limits=['No scrolling result or physical HDMI observation from this attempt','Ftdisk49 remains','No whole FATX allocation audit','Historical boot intermittency and shutdown-popup limitations remain','No save/reload, sound, game FPS, graphics API trace or GPU qualification'],pins={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file() and p.suffix in ['.py','.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
