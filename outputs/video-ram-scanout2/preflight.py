"""Freeze the unique direct-DDI attempt and reject any changed input or reused run."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['control001','candidate001'];out=k/case
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
f=read(k/('fixture-'+case+'.json'));review=read(k/'pe-review.json')
assert not (out/'preflight.json').exists() and not (ws/('work/runs/nt5-vrscan2-'+case)).exists()
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/('work/video-ram-scanout2-'+case+'-seed.qcow2'))==f['seed_sha256']
assert review['passed'] and sha(k/'pe-review.json')==f['pe_review_sha256']
assert sha(k/'probe.c')==review['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==review['probe_sha256']
assert sha(k/'candidate001/artifacts/xwnram.dll')==review['display_sha256']
assert sha(k/'build-report.json')==review['build_sha256']
assert read(k/'source-verification.json')['passed']
assert read(k/'source-verification.json')['build_sha256']==review['build_sha256']
assert read(out/'before-configuration.json')['expected_configuration']
assert sha(out/'registry-selection.json')==f['registry_selection_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
patch=read(k/'patch-review.json');assert sha(k/'0108-ram-primary.patch')==patch['patch_sha256']
for n,h in patch['source_files'].items():assert sha(k/'display'/n)==h
paths=[p for p in k.iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.md','.patch','.json'] and not p.name.startswith('fixture-')]
paths += [k/('fixture-'+case+'.json')]+list((k/'display').iterdir())+list((k/'tests').iterdir())
snapshot=out/'source';snapshot.mkdir(exist_ok=False);pins={}
for p in paths:
 n=p.relative_to(k);target=snapshot/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());pins[n.as_posix()]=sha(p)
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,debugger=True,sources=pins,
 probe_sha256=review['probe_sha256'],display_sha256=review['display_sha256']),indent=2)+'\n')
print('Pinned direct-DDI attempt; no physical access')
