"""Freeze crash003 once; a deliberate crash is never ordinary qualification."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];assert sys.argv[1]=='crash003';out=k/'crash003'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
f=read(k/'fixture-crash003.json');assert sha(k/'nvnet-review.json')==f['nvnet_review_sha256'];b=read(k/'build-review.json');assert b['passed'] and sha(k/'build-review.json')==f['build_review_sha256']
for n,h in b['sources'].items():assert sha(k/n)==h
for n,row in b['binaries'].items():assert sha(k/'artifacts'/n)==row['sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
assert sha(ws/'work/nvnet-controlled-dump-crash003-seed.qcow2')==f['seed_sha256']
for n,m in read(k/'modules.json').items():assert sha(Path(m['path']))==m['sha256']
assert read(out/'before-configuration.json')['expected_configuration']
assert read(out/'before-pagefile-map.json')['requested_65536']==[dict(byte_length=65536,volume_byte_offset=140436013056),dict(byte_length=0,volume_byte_offset=0)]
names=['trigger.c','probe.c','Build.ps1','review.py','build-review.json','prepare.py','setup-origin.py','common.py','configuration.py','cold-map.py','Run.ps1','preflight.py','trace.py','supervise.py','atomic_json.py','modules-review.py','modules.json','kernel-review.json','layouts.json','fatx-review.json','nvnet-review.json','fixture-crash003.json']
snap=out/'source';assert not snap.exists();snap.mkdir()
for n in names:(snap/n).write_bytes((k/n).read_bytes())
r=dict(case='crash003',scope=__doc__,passed=True,physical_access=False,intentional_crash=True,ordinary_qualified=False,sources={n:sha(k/n) for n in names},before_configuration_sha256=sha(out/'before-configuration.json'),before_map_sha256=sha(out/'before-pagefile-map.json'))
(out/'preflight.json').write_text(json.dumps(r,indent=2)+'\n');print('Pinned single intentional crash attempt; no physical access')
