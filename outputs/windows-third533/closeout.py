"""Close the finite third run and join the observed three-run sequence."""
import json,hashlib,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;PRE=K.parent/'windows-pair532'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
a=read(K/'audit.json');c=read(K/'after.json');o=read(K/'observer.json');z=read(PRE/'final001.json')
assert a['closed'] and a['hives_clean'] and a['ordinary_code_exact'] and c['completed'] and z['closed']
assert a['source_sha256']==read(K/'audit-review001.json')['sha256']==sha(K/'audit.py')
assert o['at_dashboard'] and o['windows_desktop_observed'] and not o['manual_reset_reported']
assert all(read(K/f'supervisor-{x}.json')['closed'] for x in ['launch','collect'])
for p,h in read(K/'preflight001.json')['pins'].items():assert sha(Path(p))==h,p
assert a['events']['system']['normal_shutdown_delta']==1
startup=[r for r in a['events']['system']['new_records'] if r['source']=='EventLog' and r['event_id']==6005]
assert len(startup)==1
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_launches_this_kit=1,total_sequence_launches=3,
       sequence=['cold reported -> Windows desktop -> normal restart','after Windows restart -> black -> dashboard, ten collected files unchanged','after failed launch return -> Windows desktop -> normal restart'],
       selected_disk_bytes_before_failed_second_and_successful_third_identical=True,
       third_new_startup_records=len(startup),third_normal_shutdown_delta=1,
       third_Ftdisk49=sum(x['source']=='Ftdisk' and x['event_id']==49 for x in a['events']['system']['new_records']),
       all_hives_clean=True,ordinary_launcher_startup_720p_unchanged=True,no_host_file_or_trace_reset=True,
       no_intervening_power_cycle_reported=True,no_temporary_hook=True,console_C_accessed=False,
       strict_clean_event_pass=False,deterministic_alternation_proved=False,cause_identified=False,
       boot_fix_or_stability_qualified=False,gpu_game_qualified=False,automation_remains_paused=True,
       console_last_report='UnleashX after requested normal restart; readback authenticated',
       fourth_launch_planned=False,all_owned_host_processes_closed=True,
       pins={str(p):sha(p) for p in [K/'audit.json',K/'after.json',K/'observer.json',K/'launch.json',PRE/'final001.json',PRE/'audit1.json',PRE/'audit2.json']},
       source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['closed','third_new_startup_records','third_normal_shutdown_delta','third_Ftdisk49']}))
