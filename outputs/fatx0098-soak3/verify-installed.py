"""Read-only installed-state verification after an interrupted soak; no qualification override."""
import json
from physical import k,connect,owner,get,checks,passed,save,sha,utc,startup,baseline,directory,expected,driver
q=json.loads((k/'qualification.json').read_text())
trial=json.loads((k/'physical.json').read_text());assert not trial['startup_enabled']
with connect() as f:
    owner(f);rows=checks(f,True)
    r=dict(scope=__doc__,verified_utc=utc(),checks=rows,startup_sha256=sha(get(f,startup)),
           rollback_sha256=sha(get(f,directory+'/rollback.sys')),probe_sha256=sha(get(f,directory+'/probe.exe')),
           strict_soak_passed=q['passed'],installed_candidate='FATX0098',video='0093 unchanged',new_windows_launch=False)
    r['original_0088_rollback_sha256']=sha(get(f,'/F/xwneof98/rollback.sys'))
    r['passed']=r['original_0088_rollback_sha256']=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336' and passed(rows) and r['startup_sha256']==baseline['startup_sha256'] and r['rollback_sha256']==expected[driver] and r['probe_sha256']==trial['probe_sha256']
    save(r,k/'installed-state.json');assert r['passed'];print('Installed state verified; normal startup restored, drivers/rollback intact; interrupted soak remains unqualified')
