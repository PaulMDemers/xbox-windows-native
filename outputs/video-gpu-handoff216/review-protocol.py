"""Freeze fresh216 inputs only after actual cold preparation and source review."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'protocol-review.json';frozen=k/'emulator-frozen.json'
assert not dest.exists() and not frozen.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(k/'source-review.json')['passed'];pins={}
for p in sorted(k.glob('*.py')):
 ast.parse(p.read_text(encoding='utf-8'));pins[p.relative_to(ws).as_posix()]=sha(p)
for n in ['Invoke-216.ps1','Run.ps1','build-review.json','registers.h','gpu_snapshot.c','model-inventory.json','handoff-inventory.json','source-review.json','native-input-review.json','fixture-control001.json','fixture-candidate001.json']:
 p=k/n;pins[p.relative_to(ws).as_posix()]=sha(p)
for case in ['control001','candidate001']:
 f=read(k/('fixture-'+case+'.json'));assert f['prepared'] and not f['guest_launch'] and not f['physical_access']
 assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
 p=k/'artifacts/build001'/case/'xboxvnt5.sys';assert sha(p)==read(k/'build-review.json')['binaries'][case]['sha256'];pins[p.relative_to(ws).as_posix()]=sha(p)
 a=read(k/('emu-'+case)/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
a,b=[read(k/('fixture-'+c+'.json')) for c in ['control001','candidate001']]
assert a['parent_sha256']==b['parent_sha256'] and a['device_policy']==b['device_policy']
delta=[n for n in set(a['files'])&set(b['files']) if a['files'][n]!=b['files'][n]]
assert sorted(delta)==sorted(['F/winnt/system32/drivers/xboxvnt5.sys','F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'])
frozen.write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),frozen_sha256=sha(frozen),pins=pins,common_file_delta=delta,
 physical_access=False,guest_launch=False,gpu_submission=False,
 limits='Fresh216 OFF/ON observational snapshots and unique startup/helper paths. No borrowed fixture changes or relaxed event gates; no context grant or physical qualification.'),indent=2)+'\n',encoding='utf-8')
print('Fresh216 immutable inputs/protocol PASS:',len(pins))
