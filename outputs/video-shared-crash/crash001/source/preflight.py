"""Freeze a single intentional shared framebuffer crash; no physical action."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];assert sys.argv[1]=='crash001';out=k/'crash001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
assert not (out/'preflight.json').exists() and not (ws/'work/runs/nt5-video-shared-crash-crash001').exists()
f=read(k/'fixture-crash001.json');b=read(k/'build-review.json');assert b['passed'] and sha(k/'build-review.json')==f['build_review_sha256']
for n,h in b['sources'].items():assert sha(k/n)==h
for n,row in b['binaries'].items():assert sha(k/'artifacts'/n)==row['sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/'work/video-shared-crash-crash001-seed.qcow2')==f['seed_sha256']
assert sha(k.parent/'video-shared-trace2/verification.json')==f['alias_verification_sha256']
for n,m in read(k/'modules.json').items():assert sha(Path(m['path']))==m['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
assert read(out/'before-pagefile-map.json')['requested_65536']==[dict(byte_length=65536,volume_byte_offset=140436013056),dict(byte_length=0,volume_byte_offset=0)]
names=[p.name for p in k.iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.c','.md','.json']]
snap=out/'source';snap.mkdir(exist_ok=False)
for n in names:(snap/n).write_bytes((k/n).read_bytes())
(out/'preflight.json').write_text(json.dumps(dict(passed=True,physical_access=False,intentional_crash=True,ordinary_qualified=False,sources={n:sha(k/n) for n in names}),indent=2)+'\n')
print('Pinned single intentional shared framebuffer crash')
