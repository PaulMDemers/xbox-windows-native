"""Prelaunch source/fixture pins and narrow214 adapter differences."""
import ast,difflib,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'protocol-review.json';frozen=k/'emulator-frozen.json'
assert not dest.exists() and not frozen.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(k/'source-review002.json')['passed'] and read(k/'build-review.json')['passed'] and read(k/'host-tests002.json')['passed'] and read(k/'parser-tests.json')['passed']
pins={};changes={}
for p in sorted(k.glob('*.py')):
 ast.parse(p.read_text(encoding='utf-8'));pins[p.relative_to(ws).as_posix()]=sha(p)
 old=k.parent/'video-upload-runtime211'/p.name
 if old.exists():changes[p.name]=''.join(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='211/'+p.name,tofile='214/'+p.name))
for name in ['Invoke-214.ps1','Run.ps1','build-review.json','snapshot_trace.py','fixture-control001.json','fixture-candidate001.json','model-inventory.json','native-input-review.json','gpu_snapshot.c','registers.h','host-shim/ntddk.h','host-test.c','host-test002.c','source-review002.json','host002-provenance.json']:
 p=k/name;pins[p.relative_to(ws).as_posix()]=sha(p)
for case in ['control001','candidate001']:
 f=read(k/('fixture-'+case+'.json'));assert f['prepared'] and not f['guest_launch'] and not f['physical_access']
 assert sha(Path(f['fixture_path_windows']))==f['seed_sha256']
 p=k/'artifacts/build001'/case/'xboxvnt5.sys';assert sha(p)==read(k/'build-review.json')['binaries'][case]['sha256']
 pins[p.relative_to(ws).as_posix()]=sha(p)
 a=read(k/('emu-'+case)/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
for name in ['common.py','boundary_analysis.py','upload_analysis.py','runner_analysis.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','interval_policy.py','typed-state.py']:
 assert (k/name).read_bytes()==(k.parent/'video-upload-runtime211'/name).read_bytes()
assert "uploads(v,1)" in (k/'audit-emulator.py').read_text()
assert "snapshot_trace((art/'after-xwn-video-trace.bin').read_bytes(),int(case=='candidate001'))" in (k/'audit-emulator.py').read_text()
assert 'video-gpu-state214/audit-emulator.py' in (k/'run-emulator.py').read_text()
control,candidate=[read(k/('fixture-'+c+'.json')) for c in ['control001','candidate001']]
assert control['parent_sha256']==candidate['parent_sha256'] and control['device_policy']==candidate['device_policy']
allowed=['F/winnt/system32/drivers/xboxvnt5.sys','F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd']
delta=[name for name in set(control['files'])&set(candidate['files']) if control['files'][name]!=candidate['files'][name]]
assert sorted(delta)==sorted(allowed),delta
frozen.write_text(json.dumps(pins,indent=2)+'\n')
dest.write_text(json.dumps(dict(passed=True,physical_access=False,guest_launch=False,gpu_submission=False,
 source_sha256=sha(Path(__file__)),frozen_sha256=sha(frozen),pins=pins,adapter_diffs=changes,common_file_delta=delta,
 limits='Prelaunch source/fixture guards, not execution. Exact retained211 GDI/policy parsers; accounting ON both. Only native214 observational snapshot OFF/ON and unique helper/startup paths.'),indent=2)+'\n')
print('Fresh214 protocol/adapters/immutable inputs frozen PASS:',len(pins))
