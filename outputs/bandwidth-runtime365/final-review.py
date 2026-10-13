import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'candidate001';run=Path('E:/xwn365/runs/nt5-bandwidth365-candidate001');a=read(out/'audit.json');c=read(out/'closure.json')
assert c['closed'] and c['audit_sha256']==sha(out/'audit.json') and read(run/'host-exit.json')['passed'] and (run/'cleanup.json').exists()
pins=read(out/'emulator-frozen.json')
for n,h in pins.items():assert sha(W/n)==h,n
f=read(out/'fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
captures={p.relative_to(out/'artifacts').as_posix():sha(p) for p in (out/'artifacts').rglob('*') if p.is_file()}
r=dict(evidence_complete=True,closed=True,audit_sha256=sha(out/'audit.json'),captures=captures,frozen_inputs=len(pins),
 scoped_combined_passed=a['scoped_combined_passed'],strict_qualification_passed=a['strict_qualification_passed'],memory_state_passed=a['memory_state_passed'],bandwidth_passed=a['bandwidth_passed'],bandwidth_samples=a['bandwidth_samples'],
 memory_states=a['memory_states'],warnings_errors=a['warnings_errors'],normal_shutdown_count=a['normal_shutdown_count'],integrity_passed=a['integrity_passed'],
 physical_access=False,physical_qualified=False,performance_qualified=False,release_qualified=False,
 limits='Sampled current emulator memory policy, no TLB/alias completeness or hardware extrapolation; historical failures unchanged.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('355 closed; memory',r['memory_state_passed'],'combined',r['scoped_combined_passed'],'strict',r['strict_qualification_passed'])
