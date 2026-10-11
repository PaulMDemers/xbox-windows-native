"""Complete unperformed metadata stages, keep failed original audit/trace intact."""
import importlib.util,subprocess
from common import *
out=k/'preserve001';art=out/'artifacts';dest=out/'audit-remainder001.json';assert not dest.exists()
state=read(out/'host-state.json');assert state['closed'] and state['audit_exit_code']==1
assert not (out/'audit.json').exists() and not (out/'allocation.json').exists() and not (out/'device-state.json').exists()
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/phase244-runs/nt5-phase244-preserve001')
assert read(run/'host-exit.json')['passed']
f=read(k/'fixture-preserve001.json')
p=k.parent/'gpu-reference-pair243/preserve001/artifacts/before-system';assert sha(p)==f['files']['F/winnt/system32/config/system']
assert not (art/'before-system').exists();(art/'before-system').write_bytes(p.read_bytes())
subprocess.run([sys.executable,str(k/'typed-state.py'),'preserve001'],check=True)
scan(run/'hdd.qcow2',art)
r=dict(scope=__doc__,physical_access=False,original_audit_exit_code=1,original_trace_passed=False,original_results_not_rewritten=True,raw_guest_data_not_recollected=True,protected_hash_results_unrecorded=True,strict_qualification_passed=False,ordinary_qualified=False,native_gpu_ownership=False,source_sha256=sha(Path(__file__)),typed_state=read(out/'device-state.json'),allocation=read(out/'allocation.json'),hives=[])
for name in HIVES:r['hives'].append(dict(name=name,**hive(art/('after-'+name))))
spec=importlib.util.spec_from_file_location('log222',k.parent/'video-resident-context222/analyze-log.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
r['cached_workload']=parser.analyze((art/'result.log').read_bytes())
r['new_events']={}
for label in ['system','application']:
 before=read(out/('before-'+label+'-events.json'))['records'];after=read(out/('after-'+label+'-events.json'))['records'];boundary=max((v['record'] for v in before),default=0)
 r['new_events'][label]=[v for v in after if v['record']>boundary]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['warnings_errors']=[v for rows in r['new_events'].values() for v in rows if v['type'] in [1,2]]
r['inputs']={p.relative_to(ws).as_posix():sha(p) for p in art.glob('*') if p.is_file()}
r['completed_unperformed_metadata_stages']=True
save(dest,r)
print('244 unfinished metadata audit completed; original trace/audit failure retained, protected result unknown')
