"""Review actual partial233 lifecycle and failed protocol, exact staged/frozen bytes."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
for n,h in read(k/'emulator-frozen.json').items():assert sha(ws/n)==h,n
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');t=read(k/'trace001/trace.json');q=read(k/'wait-review002.json');c=read(k/'trace001/closure.json')
assert h['closed'] and h['cleanup_record_exists'] and c['closed'] and c['never_relaunch_or_recollect']
assert h['runner_exit_code']==h['tracer_exit_code']==h['audit_exit_code']==0 and h['observer_exit_code']==1
assert h['observer_failed_before_collection'] and t['closed'] and 'lock contention bound' in t['error']
assert not a['windows_launch_record_exists'] and not a['normal_shutdown_count'] and not a['dashboard_return']
assert not (k/'trace001/launch.json').exists()
assert 'preserve_result' not in t and not t.get('request_may_be_accepted')
assert not any(v['command']=='stop' or v['command'].startswith('qom-set') for v in t['monitor'])
assert a['integrity_passed'] and not a['new_events']['system'] and not a['new_events']['application']
for n in ['cpu_scope_passed','observation_scope_passed','strict_qualification_passed','backend_preservation_qualified','ordinary_qualified','physical_qualified']:assert not a[n]
assert not t['remaining_breakpoints']
assert q['passed'] and not q['complete_observation_protocol'] and q['waited_at_stop'] is None
assert q['trace_sha256']==sha(k/'trace001/trace.json') and q['source_sha256']==sha(k/'decode-wait002.py')
assert len(q['views'])==1 and q['unique_events']==256
assert len(q['producer_pairs'])==len(q['ack_pairs'])==len(q['complete_captured_lifecycles'])==51
assert all(v['cleared_nop'] for v in q['ack_pairs'])
assert not q['missing_pair_boundaries'] and not q['reset_pairs']
v=q['views']['wait_live_first'];assert v['header']['total']==16682 and v['header']['overwritten']==16426
assert v['rows'][0]['kind']==5,'Leading unmatched acknowledgement retained'
assert all(r['parameter']==0x7a080101 and r['trapped']==0x100 and r['nsource']==1 for r in q['producer_pairs'])
assert q['error_mask']==0x100000
busy=[v for v in t['monitor'] if 'xwn-wait233-report' in v['command'] and 'busy=1' in v['reply']]
assert len(busy)==20 and all('lock=2' in v['reply'] for v in busy)
for n in ['before/allocation.json','allocation.json']:
    al=read(k/'trace001'/n);assert al['files']==6719 and al['directories']==320 and al['directory_clusters']==321
    assert al['allocation_consistent'] and not al['errors'] and not al['orphan_cluster_count']
assert read(k/'trace001/before/allocation.json')==read(k/'trace001/allocation.json')
assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives'])
assert not read(k/'test001.json')['passed'] and read(k/'test002.json')['passed']
test=read(k/'test002.json');assert test['build']=='build002' and len(test['runs'])==2
assert all(row['exit_code']==0 and not row['stderr'] and 'records=100000' in row['stdout'] for row in test['runs'])
assert test['source_sha256']==sha(k/'test-wait.py') and test['test_sha256']==sha(k/'test-wait.c')
assert test['actual_helper_sha256']==sha(k/'artifacts/test002/wait-actual.inc')
assert test['actual_row_sha256']==sha(k/'artifacts/test002/row-actual.inc')
assert read(k/'prelaunch-review002.json')['passed'] and read(k/'guard-test001.json')['passed']
assert read(k/'prelaunch-failure001.json')['source_sha256']==sha(k/'prelaunch-review.py')
for build,manifest,patch,script,generator in [('build001','candidate001-source-pins.json','wait233-build001.patch','build.py','patch.py'),('build002','candidate002-source-pins.json','wait233-build002.patch','build002.py','patch002.py')]:
    b=read(k/(build+'.json'));pins=read(k/manifest)
    assert b['passed'] and b['borrowed_sources_restored'] and len(b['original_sources'])==7
    assert b['source_sha256']==sha(k/script) and b['patch_generator_sha256']==sha(k/generator)
    assert b['source_manifest_sha256']==sha(k/manifest) and b['patch_sha256']==sha(k/patch)
    assert b['executable_sha256']==sha(k/'artifacts'/build/'xemu-preserve227.exe')
    for f in (k/'artifacts'/build/'source').rglob('*'):
        if f.is_file():assert sha(f)==pins[f.relative_to(k/'artifacts'/build/'source').as_posix()]
count=read(k/'allocation-count-correction001.json');old=k.parent/'xemu-backend-consume232/trace001/allocation.json'
assert count['allocation_sha256']==sha(old) and count['actual_files']==read(old)['files']==6724
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for pid in [h[n] for n in ['controller_pid','runner_pid','tracer_pid','observer_pid']]:
    r=subprocess.run(['pwsh','-NoProfile','-Command',f'if(Get-Process -Id {pid} -ErrorAction SilentlyContinue){{exit 1}}'],capture_output=True)
    assert r.returncode==0,('Owned PID exists',pid)
staged={}
for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0'):
    if n.startswith('outputs/xemu-wait-lifecycle233/'):
        blob=subprocess.check_output(['git','show',':'+n],cwd=ws);assert blob==(ws/n).read_bytes(),n
        staged[n]=hashlib.sha256(blob).hexdigest()
assert staged
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),staged_byte_pins=staged,frozen_inputs_unchanged=True,owned_root_processes_closed=True,actual_partial_lifecycles_verified=51,full_observation_protocol=False,windows_launched=False,physical_access=False,
    scope='Actual read-only partial runtime journal and preserved observer failure. Host adapter checks/selected cold integrity only; no handoff/Windows/native GPU qualification.'),indent=2)+'\n')
print('233 partial lifecycle/failed protocol/frozen/staged bytes and repository checks PASS')
