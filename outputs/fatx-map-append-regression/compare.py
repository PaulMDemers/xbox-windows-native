"""Compare the fresh settled-device pair without waiving recurring event failures."""
import subprocess,sys
from common import *
assert not (k/'comparison.json').exists()
for case in ['mode0','mode0b','settled0','settled1']:
    subprocess.run([sys.executable,str(k/'verify-evidence.py'),case],check=True)
fixtures=[read(k/('fixture-'+c+'.json')) for c in ['settled0','settled1']]
a,b=fixtures
assert a['parents']==b['parents'] and a['protected']==b['protected'] and a['preserved_hives']==b['preserved_hives']
assert a['build_review_sha256']==b['build_review_sha256'] and a['startup_sha256']==b['startup_sha256']
assert a['payloads'][0]['sha256']==b['payloads'][0]['sha256']
pre=[read(k/c/'preflight.json') for c in ['settled0','settled1']]
for name,h in pre[0]['sources'].items():
    if not name.startswith('fixture-'):assert pre[1]['sources'][name]==h
audits=[read(k/c/'audit.json') for c in ['settled0','settled1']]
r=dict(scope=__doc__,same_parent_and_helper=True,physical_access=False,debugger=False,cases=[])
for case,a in zip(['settled0','settled1'],audits):
    r['cases'].append(dict(case=case,mode=a['mode'],workload_and_persistence_passed=a['workload_and_persistence_passed'],integrity_passed=a['integrity_passed'],strict_events_passed=a['strict_events_passed'],strict_qualification_passed=a['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],new_warning_error_count=len(a['warnings_errors']),recurring_exact_count=len(a['recurring_exact_baseline']),audit_sha256=sha(k/case/'audit.json'),launch=read(k/case/'launch.json')['cycles'][0]))
r['exact_final_bytes_equal']=all(x['matched'] and y['matched'] and x['sha256']==y['sha256'] for x,y in zip(audits[0]['files'],audits[1]['files']))
r['both_bounded_workloads_passed']=all(a['workload_and_persistence_passed'] and a['integrity_passed'] for a in audits)
r['both_strict_qualified']=all(a['strict_qualification_passed'] for a in audits)
r['limits']='Each ordinary run covers936 mapping/unmap/EOF cycles and13 final cold files, not arbitrary concurrency or power interruption. Strict recurring service errors remain failures. Settled emulator policy is inherited; no physical or release promotion.'
save(k/'comparison.json',r);print(json.dumps(r,indent=2))
