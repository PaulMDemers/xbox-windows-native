"""Close failed482 without inventing Windows execution or a depth result."""
import hashlib,json
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(K/'physical001-stage.json');c=read(K/'physical001-collection.json');v=read(K/'cold-review001.json');p=read(K/'package001.json')
assert s['completed'] and c['completed'] and c['hook_removed'] and not c.get('result_directory')
assert v['selected_cold_audit_passed'] and v['primary']['preparation_verified'] and not v['refusal_present']
assert all(not e['new_records'] and e['normal_shutdown_delta']==0 for e in v['events'].values())
for n,b in s['before'].items():assert c['files'][n]['sha256']==b['sha256']
for name,h in p['dependencies'].items():assert sha(Path(name))==h
for row in c['files'].values():
 if row:assert sha(Path(row['path']))==row['sha256']
raw=Path(c['files']['/E/Applications/XWNBoot482a/report.bin']['path']).read_bytes();neg=0
for length in range(176):
 try:decode(raw[:length])
 except ValueError:neg+=1
 else:raise AssertionError('Truncation accepted')
r=dict(closed=True,scoped_depth_passed=False,Windows_sample_receipts_observed=False,windows_entry_proved=False,normal_windows_restart_proved=False,strict_system_qualification=False,physical_launches=1,hook_removed=True,console_C_accessed=False,boot_preparation=v['primary'],selected_cold_audit_passed=True,all_before_files_unchanged=True,new_events=v['events'],actual_primary_truncation_negatives=neg,frozen_dependencies_exact=True,archived_inputs=read(K/'archived-inputs001.json'),failure='Dashboard returned without Windows workload receipts; preparation trace cannot prove paging transition',all_owned_processes_closed=True,boot_failure_root_cause='unresolved',private_files={str(f):dict(bytes=f.stat().st_size,sha256=sha(f)) for f in Path('C:/xwn482').rglob('*') if f.is_file()})
out.write_text(json.dumps(r,indent=2)+'\n');print('482 closed incomplete launch, cold baseline exact, no depth qualification.')
