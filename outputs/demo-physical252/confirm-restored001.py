"""Final read-only dashboard and captured-baseline confirmation before queue release."""
from common001 import *
pins();out=k/'restored001';dest=out/'confirmation.json';assert not dest.exists()
restored=read(out/'restoration.json');allocation=read(out/'allocation.json');scan=read(out/'scan.json');returned=read(out/'scan-return.json')
assert restored['completed'] and restored['baseline_restored'] and all(restored['checks'].values())
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert scan['collected'] and scan['snapshot_complete'] and returned['dashboard_return']
r=dict(scope=__doc__,physical_writes=False,created_utc=utc(),checks={},passed=False,source_sha256=sha(pathlib.Path(__file__).read_bytes()))
with connect() as f:
    r['protected_components']=check_fixed(f)
    paths=[startup]
    for path in before()['files']:
        if '/winnt/system32/config/' in path.lower() and path.rsplit('/',1)[1].lower().split('.')[0] in ['system','software','sam','security','default']:paths.append(path)
        if '/winnt/system32/drivers/' in path.lower():paths.append(path)
    for path in dict.fromkeys(paths):
        data=get(f,path);expected=sha(incoming(path));r['checks'][path]=dict(sha256=sha(data),expected=expected,matched=sha(data)==expected)
        assert sha(data)==expected,'Restored baseline drift: '+path
    initial={n.lower() for n,row in before()['inventories']['/F/winnt/inf'].items() if not row['directory']}
    current={n.lower() for n,row in names(f,'/F/winnt/inf').items() if not row['directory']}
    assert current==initial,'INF inventory drift';r['inf_inventory_exact']=True
    driver_names={n.lower() for n in names(f,'/F/winnt/system32/drivers')}
    assert ('xwnaci207.sys' in driver_names)==before()['target_driver_initially_present']
    r.update(passed=True,dashboard_owner_verified=True,completed_utc=utc(),allocation_consistent=True,orphan_clusters=0,all_prior_restoration_readbacks_passed=True,retained_inactive_trial_directories=['/F/xwnd252i','/F/xwnd252p','/E/Applications/XWND252scanI','/E/Applications/XWND252scanP','/E/Applications/XWND252scanR'])
save(dest,r);print('Final incoming baseline/startup readback and dashboard identity verified; no console writes',flush=True)
