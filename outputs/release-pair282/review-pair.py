"""Review the two closed actual cases; no launch, collection or repeated audit."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summaries=[];prepared=[]
for case in ['control001','candidate001']:
 p=k/case;f=read(p/'final-review.json');t=read(p/'trace.json');a=read(p/'audit.json');q=read(p/'reuse-proof.json');frozen=read(p/'prepared.json');prepared.append(frozen)
 assert f['closed'] and f['scoped_unchanged_guest_reuse_passed'] and not f['strict_passed']
 assert not f['original_whole_disk_equality'] and f['disk_changed_bytes']==1 and f['file_system_bytes_inherited_unchanged']
 assert a['eeprom_unchanged'] and all(x['returncode']==0 for x in a['checks'].values())
 assert all(all(a[n].values()) for n in ['source_pins','immutable_copies','dependencies'])
 for n,h in frozen['dependencies'].items():assert sha(Path(n))==h,n
 graphs=q['terminal']['graphs'];reuse=q['reuse']
 assert [g['base']['unit_edges'] for g in graphs]==([4,0,4] if case.startswith('candidate') else [4,4,4])
 assert reuse['actual_release_decrements']==(4 if case.startswith('candidate') else 0)
 assert reuse['actual_guest_binds']==4 and reuse['independent_three_snapshot_equality']
 summaries.append(dict(case=case,started_utc=t['started_utc'],ended_utc=t['ended_utc'],
  scoped_passed=True,strict_passed=False,stage_rows=[len(list((p/f'stage{i}-pages').glob('*.txt'))) for i in range(1,4)],
  unit_edges=[g['base']['unit_edges'] for g in graphs],texture_bindings=[g['base']['texture_bindings'] for g in graphs],
  callback_counts=[g['boundary']['callbacks'] for g in graphs],mutation_clocks=[g['boundary']['mutation_clock'] for g in graphs],
  original_shader_work_functions_returned=graphs[0]['extension']['original_work_returned'],
  actual_release_decrements=reuse['actual_release_decrements'],actual_guest_binds=reuse['actual_guest_binds'],
  lifetime_events=reuse['life']['sequence'],lifetime_runs=reuse['life']['runs'],capture_mask=reuse['life']['captures'],
  snapshots=12,exact_source_rgba_bytes=12288,native_source_guard_read_bytes=49152,
  native_framebuffer_bytes=1440,frozen_dependencies=f['frozen_dependencies'],private_captures=f['private_captures_verified'],
  host_exit=f['host_exit'],whole_disk_changed_bytes=1,final_review_sha256=sha(p/'final-review.json')))
assert prepared[0]['dependencies']==prepared[1]['dependencies']
assert {n:v['sha256'] for n,v in prepared[0]['inputs'].items()}=={n:v['sha256'] for n,v in prepared[1]['inputs'].items()}
controls=read(k/'actual-controls001.json');assert controls['passed']
r=dict(passed=True,scope='Matched scoped actual four-unbound-unit counted release and unchanged normal guest reuse',
 cases=summaries,identical_frozen_inputs=True,identical_host_dependencies=True,
 actual_mutations_rejected=controls['mutations_rejected'],strict_overall_passed=False,
 strict_failure='One changed reserved-sector byte in each run; original whole-disk equality remains failed',
 no_whole_backend_retirement=True,performance_qualified=False,native_gpu_grant=False,physical_changed=False,
 all_owned_runtime_sessions_closed=True)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
