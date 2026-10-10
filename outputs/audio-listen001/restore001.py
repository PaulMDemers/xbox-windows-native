"""Restore only captured incoming configuration/files after preserving trial evidence."""
from common001 import *
pins();out=k/'restored001';assert not out.exists(),'Preserve previous restoration attempt';out.mkdir()
record=out/'restoration.json';baseline=before()
cases=[name for name in ['install001','playback001'] if (k/name/'trial.json').exists()]
assert cases and all(read(k/n/'collection.json')['completed'] for n in cases),'Collect each attempted Windows trial first'
latest=read(k/cases[-1]/'collection.json');prior_art=k/'artifacts'/cases[-1]
r=dict(scope=__doc__,created_utc=utc(),completed=False,baseline_restored=False,writes=[],removed=[],checks={},event_and_setup_history_left_intact=True)
save(record,r)
with connect() as f:
    put(f,startup,incoming(startup));r['startup_restored']=True;save(record,r)
    # Every removed or changed byte must match the already preserved final trial.
    def preserve_check(path):
        rows=[n for n in latest['files'] if n.lower()==path.lower()];assert rows and latest['files'][rows[0]] is not None,path
        name=rows[0];data=get(f,path);assert sha(data)==latest['files'][name]['sha256'],'Post-collection file drift: '+path
        assert data==(prior_art/name.lstrip('/')).read_bytes(),'Missing exact failed/trial evidence'
        return data
    def restore(path):
        original=incoming(path);current=get(f,path)
        if current!=original:
            preserve_check(path);r['writes'].append(dict(path=path,from_sha256=sha(current),to_sha256=sha(original)));save(record,r);put(f,path,original)
        r['checks'][path]=sha(get(f,path))==sha(original);save(record,r)
    def remove(path):
        current=preserve_check(path);r['removed'].append(dict(path=path,preserved_sha256=sha(current)));save(record,r)
        f.delete(path);assert path.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,path.rsplit('/',1)[0])}
    for root in ['/F/winnt/inf','/F/winnt/system32/config']:
        original={n.lower():n for n,row in baseline['inventories'][root].items() if not row['directory']}
        now=names(f,root)
        for name,row in now.items():
            relevant=root.endswith('/inf') or name.lower().split('.')[0] in ['system','software','default','sam','security']
            if not row['directory'] and relevant and name.lower() not in original:remove(root+'/'+name)
        for lower,name in original.items():
            relevant=root.endswith('/inf') or lower.split('.')[0] in ['system','software','default','sam','security']
            if relevant:restore(root+'/'+name)
    drivers='/F/winnt/system32/drivers';original={n.lower() for n in baseline['inventories'][drivers]}
    for name,row in names(f,drivers).items():
        if not row['directory'] and name.lower() not in original:
            assert name.lower()=='xwnaci207.sys','Unexpected new driver needs review: '+name
            assert sha(get(f,drivers+'/'+name))=='c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75'
            remove(drivers+'/'+name)
    for path in baseline['files']:
        if path.lower().startswith(drivers.lower()+'/'):restore(path)
    r['protected_baseline']=check_fixed(f)
    for root in ['/F/winnt/inf','/F/winnt/system32/config']:
        relevant=lambda n:root.endswith('/inf') or n.lower().split('.')[0] in ['system','software','default','sam','security']
        expected={n.lower() for n,row in baseline['inventories'][root].items() if not row['directory'] and relevant(n)}
        observed={n.lower() for n,row in names(f,root).items() if not row['directory'] and relevant(n)}
        assert observed==expected,'Restored file inventory mismatch'
    assert get(f,startup)==incoming(startup) and all(r['checks'].values())
    r.update(completed=True,baseline_restored=True,dashboard_owner_verified=True,completed_utc=utc());save(record,r)
print('Incoming startup, hives/companions, INF and audio driver baseline restored and read back; final allocation scan pending',flush=True)
