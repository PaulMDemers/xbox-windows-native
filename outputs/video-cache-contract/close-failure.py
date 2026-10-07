"""Record the closed observer failure separately from successful resumed workload."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;o=k/'trace001';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(o/'trace.json');a=read(o/'audit.json');c=read(o/'closure.json');pre=read(o/'preflight.json')
assert t['status']=='capture_incomplete' and t['error']=="AssertionError('bounded mapping trace')"
assert t['mapping_stops']==2049 and not t['mapping_calls'] and not t['mapping_returns'] and not t['runtime_pins']
assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and a['strict_qualification_passed'] and not a['ordinary_qualified']
assert sha(Path(c['private_disk']))==c['private_disk_sha256']
for n,h in pre['sources'].items():assert sha(k/n)==h==sha(o/'source'/n)
before,after=[read(o/(p+'-pagefile-map.json')) for p in ['before','after']];assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
assert all(read(o/(p+'-configuration.json'))['expected_configuration'] for p in ['before','after'])
assert read(o/'before-bootvid.json')['sha256']==read(o/'after-bootvid.json')['sha256']
dest=k/'failure-verification.json';assert not dest.exists();dest.write_text(json.dumps(dict(diagnostic_passed=False,failure_preserved=True,workload_cold_passed=True,ordinary_qualified=False,physical_access=False,guest_resumed=True,breakpoints_removed=True,source_sha256=sha(Path(__file__)),evidence={p:sha(k/p) for p in ['trace001/trace.json','trace001/audit.json','trace001/closure.json','mapping.json']},next='New corrected observer only; never relaunch/recollect this case.'),indent=2)+'\n');print('Closed observer failure verified; resumed workload PASS remains distinct')
