"""Pin all three unique outcomes and identical guest inputs without erasing failure."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
dest=k/'history-review.json';assert not dest.exists();rows=[]
for name,want in [('video-mode-reset',True),('video-mode-trace',False),('video-mode-trace2',False),('video-mode-trace3',True)]:
 d=k.parent/name;out=d/'candidate001';v=read(d/'verification.json');assert v['passed']==want
 c=read(out/'closure.json');disk=Path(c['private_disk']);assert sha(disk)==c['private_disk_sha256']
 f=read(d/'fixture-candidate001.json')
 for row in f['parents']:
  p=Path(row['path'].replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'));assert sha(p)==row['sha256']
 for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
 rows.append(dict(kit=name,passed=v['passed'],ordinary_qualified=v.get('ordinary_qualified',False),physical_qualified=v['physical_qualified'],
  probe_sha256=sha(d/'artifacts/probe.exe'),probe_source_sha256=sha(d/'probe.c'),display_sha256=sha(out/'artifacts/xwnown.dll'),
  fixture_name=f['fixture_name'],disk_path=str(disk),fixture_sha256=f['fixture_sha256'],disk_sha256=sha(disk),verification_sha256=sha(d/'verification.json'),closure_sha256=sha(out/'closure.json'),preflight_sha256=sha(out/'preflight.json')))
for key in ['probe_sha256','probe_source_sha256','display_sha256']:assert len({r[key] for r in rows})==1
assert len({r['fixture_name'] for r in rows})==len({r['disk_path'] for r in rows})==4
reference_sets=[]
for row in rows:
 d=k.parent/row['kit'];reference_sets.append([sha(d/'candidate001/artifacts'/('ref%02d.rgb'%i)) for i in range(26)])
assert all(v==reference_sets[0] for v in reference_sets)
t=read(k/'transition-verification.json');assert t['passed']
r=dict(passed=True,scope='Evidence consistency across distinct closed ordinary and diagnostic children; first diagnostic failure retained.',cases=rows,all26_cold_references_identical=True,prior_review_failure_sha256=sha(k/'pair-review-failure.json'),transition_sha256=sha(k/'transition-verification.json'),verifier_sha256=sha(Path(__file__)))
dest.write_text(json.dumps(r,indent=2)+'\n');print('Distinct outcomes, identical guest inputs and immutable parents verified')
