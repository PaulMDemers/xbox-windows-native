"""Host-only gate checks using retained emulator logs plus deliberate corruptions."""
import json
from pathlib import Path
from workload import verify_log
k=Path(__file__).resolve().parent
reports=[json.loads((k.parent/'fatx-directory-order'/case/'audit.json').read_text()) for case in ['001','002']]
checks={}
for i,r in enumerate(reports):
    checks['retained_emulator_'+str(i+1)]=verify_log(r['log'])==(True,r['elapsed_ms'])
log=reports[0]['log']
for status in range(5):checks['wait_all_success_'+str(status)]=verify_log(log.replace('WAIT_RESULT 2 ','WAIT_RESULT '+str(status)+' '))[0]
bad={
    'timeout':log.replace('WAIT_RESULT 2 ','WAIT_RESULT 258 '),
    'partial_worker':log.replace('COUNTS 500 500 500','COUNTS 499 500 500'),
    'api_error':log.replace('ERRORS 0 0 0','ERRORS 5 0 0'),
    'missing_restart':'\n'.join(v for v in log.splitlines() if not v.startswith('NORMAL_RESTART_REQUEST')),
    'pending_install':log+'RESTART_BLOCKED_PENDING_INSTALL 258 0 0\n',
    'duplicate_complete':log+'COMPLETE 500 500 500\n',
    'malformed':log+'COUNTS not integers\n',
    'empty':''}
checks.update({name:not verify_log(value)[0] for name,value in bad.items()})
assert all(checks.values()),checks
r=dict(scope=__doc__,passed=True,checks=checks,physical_access=False)
(k/'workload-verifier-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
