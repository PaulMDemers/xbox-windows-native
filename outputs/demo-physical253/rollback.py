"""Restore only this stage's video/SYSTEM changes after preserving all trial evidence."""
from common001 import *
pins();out=k/'restored001';assert not out.exists();out.mkdir()
record=out/'restoration.json';trial=read(k/'combined001/trial.json');latest=read(k/'combined001/collection.json')
assert latest['completed'] and latest['startup_restored']
art=k/'artifacts/combined001';r=dict(completed=False,baseline_restored=False,writes=[],removed=[],created_utc=utc(),audio_installation_retained=True)
save(record,r)
with connect() as f:
    assert get(f,startup)==incoming(startup)
    def exact_current(path):
        n=next(n for n in latest['files'] if n.lower()==path.lower());row=latest['files'][n]
        data=get(f,path);assert row and sha(data)==row['sha256'] and data==(art/n.lstrip('/')).read_bytes();return data
    for path,row in trial['before_payloads'].items():
        current=exact_current(path)
        if row is None:
            r['removed'].append(dict(path=path,preserved_sha256=sha(current)));save(record,r);f.delete(path);assert get(f,path,optional=True) is None
        else:
            data=(art/'rollback'/path.lstrip('/')).read_bytes();assert sha(data)==row['sha256']
            r['writes'].append(dict(path=path,from_sha256=sha(current),to_sha256=sha(data)));save(record,r);put(f,path,data)
    root='/F/winnt/system32/config';old=before()['inventories'][root]
    original={n.lower():n for n,row in old.items() if not row['directory'] and n.lower().split('.')[0]=='system'}
    for n,row in names(f,root).items():
        if not row['directory'] and n.lower().split('.')[0]=='system' and n.lower() not in original:
            path=root+'/'+n;current=exact_current(path);r['removed'].append(dict(path=path,preserved_sha256=sha(current)));save(record,r);f.delete(path)
    for n in original.values():
        path=root+'/'+n;current=exact_current(path);data=incoming(path)
        r['writes'].append(dict(path=path,from_sha256=sha(current),to_sha256=sha(data)));save(record,r);put(f,path,data)
    r['protected_restored']=check_fixed(f)
    r.update(completed=True,baseline_restored=True,completed_utc=utc());save(record,r)
print('Post-audio incoming video/SYSTEM restored; allocation audit still required')
