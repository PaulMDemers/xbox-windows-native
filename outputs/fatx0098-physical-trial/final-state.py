"""Final read-only console verification after complete bounded physical qualification."""
import json
from physical import k,connect,owner,get,checks,passed,save,sha,utc,startup,baseline,directory,expected,driver
q=json.loads((k/'qualification.json').read_text());assert q['passed']
trial=json.loads((k/'physical.json').read_text());assert not trial['startup_enabled']
with connect() as f:
    owner(f);rows=checks(f,True)
    r=dict(scope=__doc__,verified_utc=utc(),checks=rows,startup_sha256=sha(get(f,startup)),
           rollback_sha256=sha(get(f,directory+'/rollback.sys')),probe_sha256=sha(get(f,directory+'/probe.exe')),
           installed_candidate='FATX0098',video='0093 unchanged',new_windows_launch=False)
    r['passed']=passed(rows) and r['startup_sha256']==baseline['startup_sha256'] and r['rollback_sha256']==expected[driver] and r['probe_sha256']==trial['probe_sha256']
    save(r,k/'final-state.json');assert r['passed'];print('Final console state verified; normal startup,0098 installed,0088 rollback intact,video0093 unchanged')
