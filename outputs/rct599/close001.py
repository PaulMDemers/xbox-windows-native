"""Record inspected private images and close the successful discovery fixture."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn599/pc001/cold1-002/files/xwn599')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
out=K/'final001.json';assert not out.exists()
r=read('review001.json');s=read('ntfs-phase1.json');assert r['passed'] and s['closed']
visual=dict(passed=True,method='Assistant inspected original private640x480BMPs directly:00-title is the RCT title menu,02-objective explicitly names Forest Frontiers,04-park-api-observation shows the entrance/trees/path with no dialog, MarchYear1,0guests,10000cash and pause control. No frame-rate or saved-scene equivalence inference.',
            images={n:sha(P/n) for n in ['00-title.bmp','02-objective.bmp','04-park-api-observation.bmp']})
(K/'visual-review001.json').write_text(json.dumps(visual,indent=2)+'\n')
old=json.loads((K.parent/'rct598/trace-review001.json').read_text());new=read('trace-review001.json')
comparison=dict(same_main_library_request_counts=old['library_requests']==new['library_requests'],same_main_named_export_request_counts=old['named_export_requests']==new['named_export_requests'],
                counts={n:{key:v[key] for key in ['total_entry_requests','main_image_requests','other_caller_requests']} for n,v in [('598',old),('599',new)]},
                limits='Same requested names/counts do not establish the same executed renderer or timing;598 display/input failure remains failed.')
(K/'request-comparison001.json').write_text(json.dumps(comparison,indent=2)+'\n')
result=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,owned_vm_closed=True,
            game_observation='Title and paused Forest Frontiers windowed under API-entry recorder.',
            desktop=[1024,768],client=[640,480],requests={n:new[n] for n in ['total_entry_requests','main_image_requests','other_caller_requests']},
            registry_restored=True,normal_shutdown_delta=1,forced_termination=False,capture_errors=s.get('capture_errors',[]),
            capture_race_scope='One scheduled host screenshot encountered FileNotFoundError after process_exit0 during normal VM exit. Preserved; five guest BMPs complete. No retry or closed-runtime reopening.',
            console_state='Untouched; last dashboard, no owned hook.596 SOFTWARE offline cleanup still has no subsequent Windows boot.',
            limits='PC instrumented discovery only; no matched pristine game control/overhead, exact saved-scene baseline, function return/method trace, FPS or acceleration proof.',
            pins={str(p):sha(p) for p in K.iterdir() if p.is_file()})
out.write_text(json.dumps(result,indent=2)+'\n');print('599 CLOSED: instrumented title/Forest Frontiers and normal cleanup qualified;332 API requests only')
