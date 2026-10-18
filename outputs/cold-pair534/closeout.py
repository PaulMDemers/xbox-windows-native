"""Close two new power-cycle cases; no inference of a functional fix."""
import json,hashlib,datetime
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists();runs=[]
for i in (1,2):
    ready=read(K/f'ready{i}.json');a=read(K/f'audit{i}.json');o=read(K/f'observer{i}.json')
    launch=read(K/f'launch{i}.json');before=read(K/f'before{i}.json');after=read(K/f'after{i}.json')
    assert a['closed'] and a['hives_clean'] and a['ordinary_code_exact']
    assert ready['ordinal']==i and ready['power_off_on_reported'] and ready['ready']
    assert launch['readiness_sha256']==sha(K/f'ready{i}.json') and launch['selected_files_unchanged_by_power_cycle']
    assert a['source_sha256']==sha(K/'audit.py') and before['completed'] and after['completed']
    assert o['at_dashboard'] and o['user_report_received']
    assert all(read(K/f'supervisor-{x}{i}.json')['closed'] for x in ['before','launch','after'])
    for group in [before,after]:
        for row in group['files'].values():assert sha(Path(row['path']))==row['sha256']
    events=a['events']['system'];new=events['new_records']
    runs.append(dict(ordinal=i,desktop_reported=o['windows_desktop_observed'],
        normal_shutdown_delta=events['normal_shutdown_delta'],new_startup_records=sum(e['source']=='EventLog' and e['event_id']==6005 for e in new),
        Ftdisk49=sum(e['source']=='Ftdisk' and e['event_id']==49 for e in new),
        application_popup26=sum(e['source']=='Application Popup' and e['event_id']==26 for e in new),hives_clean=True,
        changed_files=a['changed_files'],launch_utc=launch['utc']))
for p,h in read(K/'preflight001.json')['pins'].items():assert sha(Path(p))==h,p
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_launches=2,runs=runs,
    both_desktops_observed=all(x['desktop_reported'] for x in runs),
    condition='Normal Windows Restart followed by dashboard front power off about10s/on; user reported, standby rails not measured',
    same_installed_720p_launcher=True,no_host_file_reset=True,no_temporary_hook=True,remote_file_writes=[],console_C_accessed=False,
    all_owned_host_processes_closed=True,console_last_report='Dashboard after requested normal Restart; authenticated collection',
    strict_clean_event_pass=all(x['Ftdisk49']==0 and x['application_popup26']==0 for x in runs),
    general_reliability_qualified=False,cause_identified=False,functional_fix_installed=False,gpu_games_qualified=False,
    third_launch_planned=False,automation_remains_paused=True,
    pins={str(p):sha(p) for p in K.glob('*.json')},source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({n:r[n] for n in ['closed','runs','both_desktops_observed']}))
