"""Pin the new observation protocol and every invoked dependency before launch."""
import ast, hashlib, importlib.util, json, re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
frozen=read(k.parent/'surface-pending263/emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
b=read(k/'renderer-build003.json');assert b['passed'] and b['borrowed_sources_restored']
for n,h in b['inputs'].items():assert sha(k/n)==h,n
capsule=Path('E:/Codex-archive/xbox-windows-native/ledger265-build003')
assert sha(capsule/'xemu-ledger265.exe')==b['executable_sha256']
for n,h in read(k/'renderer-source-pins003.json').items():assert sha(capsule/'source'/n)==h,n
for name in ['probe-review001.json','callsite-review.json','host-tests001.json','ledger-tests001.json']:
    assert read(k/name)['passed']
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():assert sha(ws/n)==h,n
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
allocation=read(k/'emu001/before/allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
for p in k.glob('*.py'):ast.parse(p.read_text())
for n in ['kernel-discovery.py','atomic_json.py','close-host.py','typed-state.py','common.py']:
    assert (k/n).read_bytes()==(k.parent/'surface-pending263'/n).read_bytes()
old=(k.parent/'surface-pending263/attest.py').read_text()
assert (k/'attest.py').read_text()==old.replace('1<=stage<=5','1<=stage<=2').replace('[(0,0),(1,0),(2,0),(3,1),(4,1)]','[(1,0),(2,0)]')
warnings=lambda s:set(re.findall(r'warning:.*',s))
current=(k/'renderer-build003.log').read_text(errors='replace')
assert not warnings(current)-warnings((k.parent/'surface-bridge260/renderer-build001.log').read_text(errors='replace'))
spec=importlib.util.spec_from_file_location('deps265',k/'runtime-dependencies.py')
deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)
host=deps.inventory();(k/'host-dependencies.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
r=dict(passed=True,physical_access=False,guest_launched=False,debugger=True,ordinary_qualified=False,
    renderer_sha256=b['executable_sha256'],host_dependencies=len(host),inherited_frozen_inputs=len(frozen),
    changed_sources=b['changed_sources'],warning_instances=len(re.findall(r'warning:',current)),new_warning_messages=[],
    read_only=True,retirement_ready=False,native_gpu_grant=False,
    protocol='Two fully attested native checkpoints; CPU seed0 reads before/after one immutable observation. No pattern injection or disposal.',
    limits='Shader handles are UNKNOWN completion; indexed GL bindings/container attachments need later closure. No comprehensive retirement proof.')
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.json','.patch']:
        frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('265 preflight PASS;',len(frozen),'frozen inputs;',len(host),'host dependencies; no guest launched')
