"""Read-only acceptance of a bounded demo preview; strict failures remain recorded."""
from common001 import *
pins();dest=k/'accepted-state.json';assert not dest.exists()
a=read(k/'playback001/audit.json');assert a['scoped_runtime_passed'] and a['integrity_passed']
c=read(k/'playback001/collection.json');assert c['completed'] and c['startup_restored']
r=dict(passed=False,created_utc=utc(),physical_result=True,release_qualified=False,strict_qualification_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],checks={})
with connect() as f:
    r['checks']['protected']=all(check_fixed(f).values())
    r['checks']['normal_startup']=get(f,startup)==incoming(startup)
    for name in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:
        path='/F/winnt/system32/config/'+name;r['checks'][path]=sha(get(f,path))==c['files'][path]['sha256']
    path='/F/winnt/system32/drivers/xwnaci207.sys';r['checks'][path]=sha(get(f,path))==c['files'][path]['sha256']
    config=get(f,'/C/Dashboard/config.xml');r['dashboard_config_sha256']=sha(config)
    import xml.etree.ElementTree as ET
    assert len(config)-len(config.rstrip(b'\0')) in [0,1] and b'\0' not in config.rstrip(b'\0')
    xml=ET.fromstring(config.rstrip(b'\0'));entries=[n for n in xml.iter() if n.attrib.get('Action','').lower()==r'e:\applications\xwnfboot\default.xbe'.lower()]
    r['windows_menu_entries']=[dict(n.attrib) for n in entries];r['checks']['windows_menu_entry']=bool(entries)
    r['passed']=all(r['checks'].values());r['completed_utc']=utc();save(dest,r)
assert r['passed'],'Installed state differs from audited preview'
print('Unchanged-driver listening test closed; demo preview retained; normal startup and Windows menu verified; strict release status unchanged')
