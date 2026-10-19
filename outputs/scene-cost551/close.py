"""MIT. Close actual551 evidence without promoting absent or failed graphics."""
import datetime,hashlib,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def host(s):return Path('/mnt/'+s[0].lower()+s[2:].replace(chr(92),'/')) if sys.platform!='win32' and len(s)>2 and s[1]==':' else Path(s)
out=K/'final001.json';assert not out.exists()
c=read(K/'collection001.json');st=read(K/'stage001.json');a=read(K/'audit1.json');q=read(K/'package001.json');launch=read(K/'launch001.json')
assert c['completed'] and c['hook_removed'] and c['protected_code_exact']
assert st['completed'] and launch['requested'] and launch['ordinary_launcher']
assert a['closed'] and a['hives_clean'] and a['ordinary_code_exact']
for n,row in c['files'].items():assert sha(host(row['path']))==row['sha256'] and host(row['path']).stat().st_size==row['bytes'],n
for n in st['staged']:assert c['files'][n]['unchanged'],n
for n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert c['files'][n]['unchanged'],n
assert c['remote_writes']==[dict(action='rename-owned-hook',source='/E/documents and settings/all users/start menu/programs/startup/xwn551.cmd',destination='/E/xwn551-kit/startup-used.cmd')]
states={n:read(K/f'supervisor-{n}.json') for n in ['stage','launch','collect']}
assert all(v['closed'] and v['completed'] for v in states.values())
if (K/'observation001.json').exists():assert read(K/'observation001.json')['closed']
runtime=read(K/'runtime-review001.json') if (K/'runtime-review001.json').exists() else None
modules=controls=None
if runtime and runtime['all_allowed_cases_passed']:
    modules=read(K/'module-review001.json');controls=read(K/'actual-controls001.json')
    assert modules['passed'] and controls['passed'] and len(modules['rows'])==len(runtime['rows'])==6 and len(controls['rows'])==2
passed=bool(runtime and runtime['all_allowed_cases_passed'] and modules and controls)
normal=bool(runtime and runtime['runner']['restart_request']=='1' and a['events']['system']['normal_shutdown_delta']==1)
events=[dict(log=log,**e) for log,v in a['events'].items() for e in v['new_records']]
archive=host('C:/xwn551/frozen001');assert not archive.exists()
size=sum(host(p).stat().st_size for p in q['pins']);assert shutil.disk_usage(archive.parent).free-size-64*1024**2>=20*1024**3
archive.mkdir();archived=[]
for i,(n,h) in enumerate(sorted(q['pins'].items())):
    p=host(n);assert sha(p)==h;dest=archive/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
    archived.append(dict(original=n,path=str(dest),sha256=h))
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),launch_count=1,ordinary_launcher=True,
    combined_scene_passed=passed,normal_windows_restart_supported=normal,strict_system_qualification=bool(passed and normal and not any(e['type'] in (1,2) or e['source']=='Application Popup' for e in events)),
    runtime_review=runtime,module_review=modules,actual_controls=controls,hives_clean=a['hives_clean'],events=events,
    result_namespace_present='result_directory' in c,temporary_hook_removed=True,protected720p_ordinary_startup_exact=True,
    whole_allocation_audit=False,console_C_accessed=False,boot_issue_tabled=True,boot_reliability_fixed=False,
    gpu_qualified=False,game_compatibility_qualified=False,performance_qualified=False,windowed_pixel_presentation_qualified=passed,visual_observer_qualified=False,
    all_owned_supervisors_closed=True,no_next_launch_queued=True,archived_inputs=archived,
    evidence_sha256={n:sha(K/n) for n in ['package001.json','stage001.json','launch001.json','collection001.json','audit1.json']},
    source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({n:r[n] for n in ['closed','combined_scene_passed','normal_windows_restart_supported','strict_system_qualification','temporary_hook_removed']}))
