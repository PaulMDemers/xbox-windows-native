"""Read-only final console state after one collected trial and allocation scan."""
import json
from physical import k,connect,owner,get,checks,passed,sha,utc,save,startup,baseline,directory,expected,driver
p=k/'installed-state.json';assert not p.exists()
trial=json.loads((k/'physical.json').read_text());scan=json.loads((k/'scan.json').read_text())
audit=json.loads((k/'binary-audit.json').read_text())
assert trial.get('collected_utc') and not trial['startup_enabled'] and scan.get('collected_utc') and audit['complete']
with connect() as f:
    owner(f)
    r=dict(scope=__doc__,utc=utc(),dashboard_available=True,checks=checks(f,True),startup_sha256=sha(get(f,startup)),rollback_sha256=sha(get(f,directory+'/rollback.sys')))
    r['passed']=passed(r['checks']) and r['startup_sha256']==baseline['startup_sha256'] and r['rollback_sha256']==expected[driver]
    save(r,p);assert r['passed'];print('Installed0101/video0093, normal startup and0098 rollback verified; no launch')
