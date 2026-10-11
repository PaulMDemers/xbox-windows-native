"""Read-only acceptance of a bounded demo preview; strict failures remain recorded."""
from common001 import *
pins();dest=k/'accepted-state.json';assert not dest.exists()
a=read(k/'combined001/audit.json');review=read(k/'combined001/binding-transition-review.json')
assert review['supplemental_scoped_combined_passed'] and review['supplemental_integrity_passed']
assert sha((k/'combined001/audit.json').read_bytes())==review['original_audit_sha256']
assert sha((k/'combined001/device-state.json').read_bytes())==review['device_state_sha256']
assert sha((k/'artifacts/proposed-system').read_bytes())==review['before_sha256']==read(k/'binding-edit.json')['after_sha256']
assert sha((k/'artifacts/combined001/F/winnt/system32/config/system').read_bytes())==review['after_sha256']==next(v['sha256'] for v in a['hives'] if v['name']=='system')
c=read(k/'combined001/collection.json');assert c['completed'] and c['startup_restored']
r=dict(binding_transition_review_sha256=sha((k/'combined001/binding-transition-review.json').read_bytes()),original_binding_equality_failed=True,passed=False,created_utc=utc(),physical_result=True,release_qualified=False,strict_qualification_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],checks={})
with connect() as f:
    r['checks']['protected']=all(check_fixed(f,staged=True).values())
    r['checks']['normal_startup']=get(f,startup)==incoming(startup)
    for name in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:
        path='/F/winnt/system32/config/'+name;r['checks'][path]=sha(get(f,path))==c['files'][path]['sha256']
    path='/F/winnt/system32/drivers/xwnaci207.sys';r['checks'][path]=sha(get(f,path))==c['files'][path]['sha256']
    config=get(f,'/C/Dashboard/config.xml');r['dashboard_config_sha256']=sha(config)
    import xml.etree.ElementTree as ET
    # UnleashX saved this existing config with one final NUL; retain/hash raw bytes.
    r['dashboard_trailing_nuls']=len(config)-len(config.rstrip(b'\0'))
    assert r['dashboard_trailing_nuls'] in [0,1] and b'\0' not in config.rstrip(b'\0')
    xml=ET.fromstring(config.rstrip(b'\0'));entries=[n for n in xml.iter() if n.attrib.get('Action','').lower()==r'e:\applications\xwnfboot\default.xbe'.lower()]
    r['windows_menu_entries']=[dict(n.attrib) for n in entries];r['checks']['windows_menu_entry']=bool(entries)
    r['passed']=all(r['checks'].values());r['completed_utc']=utc();save(dest,r)
assert r['passed'],'Installed state differs from audited preview'
print('Combined demo preview retained; normal startup and Windows menu verified; strict release status unchanged')
