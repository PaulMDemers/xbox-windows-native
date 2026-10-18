"""Join one physical diagnostic's observations and independent cold evidence."""
import hashlib,json,struct
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(K/'stage001.json');c=read(K/'collection001.json');a=read(K/'cold-review001.json');u=read(K/'user-desktop001.json')
assert s['completed'] and c['completed'] and a['selected_cold_audit_passed'] and u['windows_desktop_reported']
assert not c['remote_writes'] and not c['console_C_accessed']
for n in list(s['staged'])+['/E/Applications/XWNEBoot/default.xbe','/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd']:assert c['files'][n]['unchanged'],n
remote='/E/Applications/XWNBoot471a';raw=Path(c['files'][remote+'/report.bin']['path']).read_bytes();d=decode(raw)
assert d['preparation_verified'] and c['files'][remote+'/refusal.bin'] is None
negatives=0
for n in range(176):
 try:decode(raw[:n])
 except ValueError:negatives+=1
 else:raise AssertionError('truncated primary accepted')
assert len(a['hives'])==5 and all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in a['hives'].values())
shutdown=a['events']['sysevent.evt']['normal_shutdown_delta']
r=dict(closed=True,physical_launches=1,desktop_user_observed=True,primary_preparation_verified=True,refusal_absent=True,
 physical_marker_success_record_captured=False,physical_busy_status_this_run_unknown=True,
 normal_shutdown_event_delta=shutdown,normal_windows_shutdown_event_proved=shutdown>0,
 original_boot_failure_explained=False,repeat_boot_stability_qualified=False,D3D_qualified=False,
 hives_clean=5,selected_cold_audit_passed=True,full_FATX_scan=False,
 boot_startup_and_candidate_unchanged=True,events=a['events'],actual_primary_truncation_negatives=negatives,
 console_C_accessed=False,no_repeat_queued=True,all_owned_controller_processes_closed=True,
 private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn472').rglob('*') if p.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='private_files'}))
