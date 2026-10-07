"""Match serial/concurrent fixtures and retain every failure as recorded."""
import subprocess,sys
from common import *
assert not (k/'comparison.json').exists()
cases=['serial001','flush001']
for case in cases:subprocess.run([sys.executable,str(k/'verify-evidence.py'),case],check=True)
fixtures=[read(k/('fixture-'+c+'.json')) for c in cases];a,b=fixtures
for name in ['parents','protected','preserved_hives','build_review_sha256','startup_sha256']:assert a[name]==b[name],name
assert a['payloads'][0]['sha256']==b['payloads'][0]['sha256']
pre=[read(k/c/'preflight.json') for c in cases]
for name,h in pre[0]['sources'].items():
    if not name.startswith('fixture-'):assert pre[1]['sources'][name]==h
audits=[read(k/c/'audit.json') for c in cases]
r=dict(same_parent_and_helper=True,physical_access=False,debugger=any(a['debugger'] for a in audits),cases=[])
for case,a in zip(cases,audits):
    r['cases'].append(dict(case=case,protocol=a['protocol_details'],workload_and_persistence_passed=a['workload_and_persistence_passed'],integrity_passed=a['integrity_passed'],strict_qualification_passed=a['strict_qualification_passed'],new_warning_error_count=len(a['warnings_errors']),recurring_exact_count=len(a['recurring_exact_baseline']),audit_sha256=sha(k/case/'audit.json'),launch=read(k/case/'launch.json')['cycles'][0]))
r['exact_final_bytes_equal']=all(x['matched'] and y['matched'] and x['sha256']==y['sha256'] for x,y in zip(audits[0]['files'],audits[1]['files']))
r['both_bounded_workloads_passed']=all(a['workload_and_persistence_passed'] and a['integrity_passed'] for a in audits)
r['both_strict_qualified']=all(a['strict_qualification_passed'] for a in audits)
r['limits']='AllocationSize changes are API observations, final chains/bytes are cold audited. Positive append-epoch coverage is not a kernel-instruction overlap trace. No hardware cause, driver fix, or error waiver.'
save(k/'comparison.json',r);print(json.dumps(r,indent=2))
