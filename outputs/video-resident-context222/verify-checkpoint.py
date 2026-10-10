"""Read-only posthoc review; never launches or recollects a closed guest."""
import hashlib,json,pathlib
kit=pathlib.Path(__file__).resolve().parent
root=kit.parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
dest=kit/'checkpoint-review.json'
assert not dest.exists(), 'Unique review record already exists'
frozen=load(kit/'emulator-frozen.json')
for name,digest in frozen.items():assert sha(root/name)==digest,name
build=load(kit/'build005.json')
for name,digest in build['source_pins'].items():assert sha(kit/name)==digest,name
for attempt in ['001','002','003']:
    for name,digest in load(kit/f'build{attempt}.json')['source_pins'].items():
        assert sha(kit/f'prior-build{attempt}'/name)==digest,(attempt,name)
assert load(kit/'build-review005.json')['passed'] and load(kit/'bridge001.json')['passed']
for name,row in build['native'].items():
    p=kit/'artifacts/build005'/name
    assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
case=kit/'runtime001';a=load(case/'audit.json');c=load(case/'closure.json')
host=load(case/'host-state.json');launch=load(case/'launch.json')
run=pathlib.Path('E:/Codex-private-artifacts/xbox-windows-feasibility/resident222-runs/nt5-resident222-runtime001')
assert c['closed'] and c['never_relaunch_or_recollect']
assert sha(case/'audit.json')==c['audit_sha256'] and sha(run/'cleanup.json')==c['cleanup_sha256']
assert host['closed'] and host['status']=='cold_audited_closed'
assert all(host[k]==0 for k in ['observer_exit_code','runner_exit_code','audit_exit_code'])
assert sha(run/'instance.json')==host['instance_sha256']
assert len(launch['cycles'])==1 and launch['cycles'][0]['status']=='accepted' and launch['cycles'][0]['dashboard_return']
rows=[line.split() for line in (case/'artifacts/result.log').read_text().splitlines()]
assert all(len(v)==4 for v in rows)
leases=[tuple(map(int,v[1:])) for v in rows if v[0]=='LEASE']
releases=[tuple(map(int,v[1:])) for v in rows if v[0]=='RELEASE']
assert len(leases)==len(releases)==64 and sorted(v[1] for v in leases)==list(range(2,66))
assert sorted((w,g) for w,g,p in leases)==sorted((w,g) for w,g,s in releases)
assert all(s==0 for w,g,s in releases)
assert all(0x100000<=p<=0x3bfc000 and p%4096==0 for w,g,p in leases)
assert all(sum(w==i for w,g,p in leases)==16 for i in range(4))
for required in ['WAIT_JOIN 3 4 0','COMPLETE_CPU_OWNER_ONLY 65 65 65','VERIFIED_JOINED 3194880 1 4','INSTALL_BEFORE_WORK 0 0 0','INSTALL_BEFORE_RESTART 0 0 0']:
    assert required.split() in rows,required
assert rows[-1]==['NORMAL_RESTART_REQUEST','222','0','0']
assert a['cpu_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
assert not a['strict_qualification_passed'] and not a['ordinary_qualified']
assert not a['physical_access'] and not a['debugger'] and not a['gpu_access'] and not a['native_deferred_cleanup_qualified']
assert len(a['files'])==28 and all(v['matched'] for v in a['files'])
assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives'])
assert not a['new_events']['application'] and len(a['warnings_errors'])==1
event=a['warnings_errors'][0]
assert event['source']=='Ftdisk' and event['event_id']==49 and event['record']==204
assert not any(v['source']=='Application Popup' for v in a['new_events']['system'])
alloc=load(case/'allocation.json')
assert alloc['allocation_consistent'] and not alloc['errors'] and not alloc['orphan_cluster_count']
assert (alloc['directories'],alloc['files'],alloc['directory_clusters'])==(320,6723,321)
fixture=load(kit/'fixture-runtime001.json')
assert sha(pathlib.Path(fixture['fixture_path_windows']))==fixture['fixture_sha256']
parent=pathlib.Path('E:/Codex-archive/xbox-windows-native/upload211/candidate001-source.qcow2')
assert sha(parent)==fixture['parent_sha256'] and fixture['inherited_null_policy'] is False
result=dict(passed=True,physical_access=False,launches=0,recollections=0,
    frozen_inputs_checked=len(frozen),raw_leases_checked=64,raw_wait_all=3,
    cpu_scope_passed=True,strict_qualification_passed=False,
    native_deferred_cleanup_qualified=False,gpu_qualified=False,host_closed=True,
    reviewed_sha256={str(p.relative_to(root)):sha(p) for p in
        [case/'audit.json',case/'closure.json',case/'host-state.json',case/'launch.json',
         case/'allocation.json',case/'artifacts/result.log',kit/'fixture-runtime001.json',pathlib.Path(__file__).resolve()]},
    limits='Posthoc pins/raw CPU log/closed audit review; not a new guest run, GPU, native fallback fault or all-file-content qualification.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['passed','frozen_inputs_checked','raw_leases_checked','cpu_scope_passed','strict_qualification_passed']}))
