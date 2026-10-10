"""Review actual ordinary pair and independent read decoding, preserving strict failures."""
import hashlib,importlib.util,json,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'pair-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
pins=read(k/'emulator-frozen.json')
for name,h in pins.items():assert sha(ws/name)==h,name
for name,h in read(k/'runtime-derivation.json')['derived'].items():assert sha(k/name)==h,name
for name,h in read(k/'runtime-derivation.json')['parents'].items():assert sha(k.parent/'video-resident-context222'/name)==h,name
for name,h in read(k/'build001.json')['input_pins'].items():assert sha(k/'prior-build001'/name)==h,name
spec=importlib.util.spec_from_file_location('ret224',k/'analyze-retirement.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
rows={}
for case in ['control001','candidate001']:
    o=k/case;f=read(k/('fixture-'+case+'.json'));a=read(o/'audit.json');c=read(o/'closure.json');host=read(o/'host-state.json');launch=read(o/'launch.json')
    run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/retirement224-runs/nt5-retirement224-'+case)
    assert c['closed'] and host['closed'] and host['cleanup_record_exists'] and (run/'cleanup.json').exists()
    assert all(host[n]==0 for n in ['observer_exit_code','runner_exit_code','audit_exit_code'])
    assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
    assert not f['inherited_null_policy'] and not a['physical_access'] and not a['debugger'] and not a['gpu_writes'] and not a['gpu_ownership_qualified']
    actual=p.analyze((o/'artifacts/retirement.log').read_bytes(),case=='candidate001');assert actual==a['retirement'] and actual['passed']
    assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
    assert a['workload']['allocations']==65 and a['workload']['verified_bytes']==3194880 and a['workload']['joined_workers']==4
    allocation=read(o/'allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
    assert len(a['hives'])==5 and all(x['parsed'] for x in a['hives']) and all(x['matched'] for x in a['files'])
    rows[case]=dict(closure_sha256=sha(o/'closure.json'),audit_sha256=sha(o/'audit.json'),host_sha256=sha(o/'host-state.json'),launch_sha256=sha(o/'launch.json'),
        log_sha256=sha(o/'artifacts/retirement.log'),reads=actual['reads'],reason_names=actual['reason_names'],raw_words=actual['raw_words'],
        scope_passed=a['observation_scope_passed'],strict_qualification_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],
        allocation={n:allocation[n] for n in ['directory_count','file_count','directory_cluster_count','errors','orphan_cluster_count']} if 'directory_count' in allocation else allocation,
        protected_files=len(a['files']),hives=len(a['hives']),accepted_utc=launch['cycles'][0]['launch_requested_utc'],dashboard_utc=launch['cycles'][0]['dashboard_return_utc'],closed_utc=host['closed_utc'])
assert rows['control001']['reads']==0 and rows['candidate001']['reads']==128
r=dict(passed=True,scope='Ordinary bounded read-only preflight and unchanged CPU lifetime/cold integrity scope',cases=rows,frozen_inputs=len(pins),
       verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),physical_access=False,gpu_writes=False,gpu_ownership_qualified=False,
       limits='No grant, producer retirement, backend drain or performance claim; strict event gates remain separate and unwaived. Selected protected hashes, not all-file content qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({c:{n:v[n] for n in ['reads','reason_names','scope_passed','strict_qualification_passed']} for c,v in rows.items()},indent=2))
