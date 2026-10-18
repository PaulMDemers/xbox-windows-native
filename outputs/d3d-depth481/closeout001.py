"""Join boot preparation, actual D3D inventory, restart and immutable input evidence."""
import hashlib,json,struct
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(K/'physical001-stage.json');c=read(K/'physical001-collection.json');v=read(K/'runtime-review001.json');controls=read(K/'actual-controls001.json');package=read(K/'package001.json')
assert read(K/'module-review001.json')['passed']
assert s['completed'] and c['completed'] and c['hook_removed'] and v['all_allowed_cases_passed'] and v['normal_restart_supported'] and controls['passed']
assert c['remote_writes']==[dict(action='rename-owned-hook',source='/E/documents and settings/all users/start menu/programs/startup/xwn481.cmd',destination='/E/xwn481-kit/startup-used.cmd')]
for n,row in c['files'].items():
 if row:
  p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
for n,row in s['staged'].items():assert c['files'][n]['unchanged']
for n in ['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert c['files'][n]['unchanged']
assert c['files']['/E/Applications/XWNBoot481a/refusal.bin'] is None
raw=Path(c['files']['/E/Applications/XWNBoot481a/report.bin']['path']).read_bytes();d=decode(raw);assert d['preparation_verified']
negative=0
for n in range(176):
 try:decode(raw[:n])
 except ValueError:negative+=1
 else:raise AssertionError('actual primary truncated data accepted')
for p,h in package['dependencies'].items():assert sha(Path(p))==h,p
for row in package['files'].values():assert sha(Path(row['path']))==row['sha256']
events=[]
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 p=Path(c['files']['/E/winnt/system32/config/'+name]['path']).with_name(label+'-events.json')
 old=Path(s['before']['/E/winnt/system32/config/'+name]['path']).with_name(label+'-events.json')
 boundary=max((x['record'] for x in read(old)['records']),default=0)
 events += [dict(log=label,**x) for x in read(p)['records'] if x['record']>boundary]
strict=not any(x['type'] in (1,2) or x['source']=='Application Popup' for x in events)
r=dict(closed=True,physical_launches=1,scoped_depth_passed=True,normal_restart_supported=True,strict_system_qualification=strict,
 depth_cases=[dict(backend=row['backend'],review=row['review']) for row in v['rows']],new_events=events,
 boot_preparation=d,actual_primary_truncation_negatives=negative,actual_depth_controls=controls,
 original_boot_failure_explained=False,repeat_boot_stability_qualified=False,
 offscreen_software_rendering_qualified=True,gpu_qualified=False,game_compatibility_qualified=False,
 hook_removed=True,original_launcher_and_startup_unchanged=True,console_C_accessed=False,
 full_FATX_scan=False,all_owned_processes_closed=True,no_next_launch_queued=True,
 module_snapshots=read(K/'module-review001.json')['rows'],
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn481').rglob('*') if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['private_files','actual_inventory_controls','new_events','boot_preparation']}))
