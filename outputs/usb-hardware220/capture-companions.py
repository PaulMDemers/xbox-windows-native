"""Complete the incoming registry rollback while still at the dashboard, before Windows."""
import zipfile
import physical as m
m.pins();r=m.read(m.RECORD)
assert r['capture_complete'] and not r['launch_requested'] and not r.get('staging_started')
assert not r.get('companions_captured')
with m.connect() as f:
    names=m.names(f,'/F/winnt/system32/config')-{'.','..'}
    assert set(m.HIVES).issubset(names)
    r['config_before_names']=sorted(names);r['companions']={}
    for name in sorted(names-set(m.HIVES)-{'appevent.evt','sysevent.evt','secevent.evt'}):
        assert '/' not in name and '\\' not in name
        key='companion-'+name;path='/F/winnt/system32/config/'+name
        r['before'][key]=m.keep('before/'+key,m.get(f,path));r['companions'][key]=path;m.save(r)
    r['before']['secevent.evt']=m.keep('before/secevent.evt',m.get(f,'/F/winnt/system32/config/secevent.evt'))
    for n in m.HIVES:assert m.get(f,m.auxiliary()[n])==m.local(r['before'][n]),'Primary hive changed'
old=m.ART/'incoming-rollback.zip';old.rename(m.ART/'incoming-rollback-initial.zip')
r['initial_rollback_sha256']=r['rollback_sha256']
files=sorted((m.ART/'before').iterdir())
with zipfile.ZipFile(old,'x',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,'before/'+p.name)
with zipfile.ZipFile(old) as z:
    assert all(z.read('before/'+p.name)==p.read_bytes() for p in files)
r.update(rollback_sha256=m.sha(old.read_bytes()),companions_captured=True);m.save(r)
print('Incoming registry companions preserved; rollback ZIP verified; no physical writes',flush=True)
