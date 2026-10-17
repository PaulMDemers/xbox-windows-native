"""Close the failed launch observation without asserting probe execution."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'final-review.json';assert not out.exists()
r=json.loads((K/'no-receipt-review001.json').read_text())
c=json.loads((K/'physical001-collection.json').read_text())
stop=json.loads((K/'observer-stop001.json').read_text(encoding='utf-8-sig'))
assert c['completed'] and c['hook_removed'] and 'result_directory' not in c
assert all(r['unchanged_hives_and_events'].values())
assert stop['stopped'] and not stop['original_observation_finally_completed']
assert sha(K/'physical001-observation.json')==stop['observation_sha256']
private={}
for p,h in r['private_files'].items():assert sha(path(p))==h;private[p]=h
package=json.loads((K/'package001.json').read_text())
for p,h in package['dependencies'].items():assert sha(path(p))==h
for row in package['files'].values():assert sha(path(row['path']))==row['sha256']
build=json.loads((K/'build002.json').read_text());assert build['exit_code']==0
for p,h in build['headers'].items():assert sha(Path(p))==h
for row in build['rows']:assert sha(Path(row['path']))==row['sha256']
process=json.loads((K/'owned-process-review001.json').read_text(encoding='utf-8-sig'))
assert process['owned_processes']==[]
result=dict(closed=True,scoped_inventory_passed=False,sample_executed=None,
 normal_windows_restart_proved=False,strict_system_qualified=False,
 hook_removed=True,protected_code_and_startup_exact=True,mode='720p',
 unchanged_hives_and_events=r['unchanged_hives_and_events'],private_files=private,
 frozen_dependencies_verified=len(package['dependencies']),payloads_verified=len(package['files']),
 observer_explicitly_stopped=True,observer_deadline_reached=False,owned_processes_open=[],
 console_C_accessed=False,limitations=['No result directory or sample receipt',
 'Failing boot stage and cause unknown','No D3D failure attribution',
 'No full allocation audit or GPU/rendering qualification','Closed attempt must not be relaunched or rearmed'])
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['closed','sample_executed','hook_removed','frozen_dependencies_verified']}))
