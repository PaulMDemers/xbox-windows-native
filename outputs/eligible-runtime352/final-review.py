"""Rehash closed evidence without recollecting; record failures as failures."""
import hashlib,json,statistics
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={};metrics={}
for case in ['control001','candidate001']:
 out=K/case;run=Path('E:/xwn352/runs')/('nt5-eligible352-'+case);a=read(out/'audit.json');c=read(out/'closure.json')
 assert c['closed'] and c['audit_sha256']==sha(out/'audit.json')
 assert read(run/'host-exit.json')['passed'] and (run/'cleanup.json').exists()
 for n,h in read(out/'emulator-frozen.json').items():assert sha(W/n)==h,n
 f=read(out/'fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
 captures={p.relative_to(out/'artifacts').as_posix():sha(p) for p in (out/'artifacts').rglob('*') if p.is_file()}
 rows[case]=dict(closed=True,audit_sha256=sha(out/'audit.json'),launch_sha256=sha(out/'launch.json'),cleanup_sha256=sha(run/'cleanup.json'),captures=captures,frozen_inputs=len(read(out/'emulator-frozen.json')),scoped_combined_passed=a['scoped_combined_passed'],strict_qualification_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],normal_shutdown_count=a['normal_shutdown_count'],integrity_passed=a['integrity_passed'])
 if a['display_workload_passed']:
  for ident in range(15):
   actual=[s['intervals'][ident] for s in a['primary_samples']];phase=[s['intervals'][ident] for s in a['large_phase_samples']]
   metrics.setdefault(str(ident),{})[case]=dict(eligible_plan_bytes=sum(v['eligible_plan_bytes'] for v in actual),fast_bytes=sum(v['fast_bytes'] for v in actual),eligible_calls=sum(v['eligible'] for v in actual),fast_calls=sum(v['fast'] for v in actual),fallback_calls=sum(v['fallback'] for v in actual),operations=[v['loops'] for v in actual],phase_ms_per_operation_medians=[statistics.median(v['elapsed_ms'][i]/v['operations'] for v in phase) for i in range(4)],wall_ms_per_operation_median=statistics.median(v['wall_ms']/v['operations'] for v in phase))
b=read(K.parent/'eligible-copy351/build001.json')
for case in rows:assert sha(Path('E:/xwn351/build001')/case/'xwnown.dll')==b['cases'][case]['sha256']
probe=read(K.parent/'eligible-copy351/probe/build001.json');assert sha(Path(probe['output_windows']))==probe['binary_sha256']
h=read(K.parent/'eligible-copy351/host001.json')
for n,v in h['files'].items():assert sha(Path('E:/xwn351/host001')/n)==v
r=dict(evidence_complete=True,cases=rows,eligible_intervals=metrics,host_private_files_rehashed=len(h['files']),scoped_pair_passed=all(v['scoped_combined_passed'] for v in rows.values()),strict_pair_passed=all(v['strict_qualification_passed'] for v in rows.values()),physical_access=False,physical_qualified=False,performance_qualified=False,release_qualified=False,limits='Fresh ordinary352 evidence only; exact351 eligible denominator. Historical349/350 failures unchanged. Both profileON; global timings do not imply physical speed. Ft49 retained.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed pair',r['scoped_pair_passed'],'strict',r['strict_pair_passed'])
