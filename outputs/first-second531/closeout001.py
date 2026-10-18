"""Cold paired review of two physical standalone launches; no network access."""
import hashlib,json,datetime
from pathlib import Path
K=Path(__file__).resolve().parent;FIRST=K.parent/'visible-dispatch528'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
first=read(FIRST/'physical001-collection.json');second=read(K/'second-collection.json')
closed=read(FIRST/'physical-final001.json');launch=read(K/'second-launch.json')
assert first['completed'] and second['completed'] and closed['closed']
assert second['protected_code_exact'] and second['remote_writes']==[] and not second['temporary_hook_installed']
assert launch['requested'] and launch['ordinal']==2 and not launch['receipt_reset_performed']
for p,h in launch['source_pins'].items():assert sha(Path(p))==h,p
for name,h in read(K/'second-controller-review001.json')['source_hashes'].items():assert sha(K/name)==h,name
assert set(first['files'])==set(second['files'])
identity={}
for n,old in first['files'].items():
    new=second['files'][n]
    for row in [old,new]:
        if row:assert sha(Path(row['path']))==row['sha256'] and Path(row['path']).stat().st_size==row['bytes']
    identity[n]=(old is None and new is None) or (old is not None and new is not None and old['sha256']==new['sha256'] and old['bytes']==new['bytes'])
assert all(identity.values()),'Changed second files require independent format/delta review'
for group in closed['hives'].values():
    assert all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in group.values())
assert all(v['normal_shutdown_delta']==0 and v['new_records']==[] for v in closed['events'].values())
supervisors={a:read(K/f'supervisor-{a}.json') for a in ['launch','observe','collect']}
assert all(v['closed'] and v['completed'] for v in supervisors.values())
one=read(K/'first-observation.json');two=read(K/'second-user-observation.json')
assert one['user_report_received'] and two['user_report_received'] and two['automatic_return_reported']
assert not one['manual_reset_between_launches'] and not two['manual_reset_reported']
r=dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_launches=2,
       identical_candidate_path_method=True,first_entry_receipt_valid=True,
       second_execution_evidence='User observed blue then red, automatic dashboard return; old receipts are not fresh execution proof',
       second_exact_red_error_unknown=True,all_14_collected_paths_identical=identity,
       hives_events='Inherited first independent cold audits apply to byte-identical second copies; no new event bytes',
       first_cold_audit_sha256=sha(FIRST/'physical-final001.json'),
       first_user=one,second_user=two,supervisors=supervisors,
       temporary_hook_installed=False,ordinary_launcher_startup_720p_unchanged=True,
       remote_cleanup_needed=False,owned_test_files_retained=True,console_C_accessed=False,
       deterministic_every_other_failure_observed=False,windows_boot_tested=False,
       boot_reliability_qualified=False,gpu_games_qualified=False,automation_remains_paused=True,
       no_next_launch_queued=True,source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['closed','physical_launches','deterministic_every_other_failure_observed','windows_boot_tested']}))
