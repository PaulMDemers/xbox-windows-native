"""Freeze exact observation-only263 and the unchanged262/261 runtime gates."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'surface-coverage262'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();read=lambda p:json.loads(p.read_text())
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
frozen=read(parent/'emulator-frozen003.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
b=read(k/'renderer-build001.json');assert b['passed'] and b['borrowed_sources_restored']
assert b['changed_sources']==['hw/xbox/nv2a/pgraph/gl/renderer.c']
exe=Path('E:/Codex-archive/xbox-windows-native/pending263-build001/xemu-pending263.exe');assert sha(exe)==b['executable_sha256']
oldpins=read(parent/'renderer-source-pins001.json');pins=read(k/'renderer-source-pins001.json')
assert pins.keys()==oldpins.keys() and [n for n in pins if pins[n]!=oldpins[n]]==b['changed_sources']
for name in ['mask-tests.json','counter-tests.json','proof-tests.json','close-tests.json']:assert read(k/name)['passed']
same=['attest.py','kernel-discovery.py','atomic_json.py','attestation-inputs001.json','close-host.py','lifecycle-proof.py','analyze-sites.py']
for name in same:assert (k/name).read_bytes()==(parent/name).read_bytes()
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():assert sha(ws/n)==h,n
for p in k.glob('*.py'):ast.parse(p.read_text())
sp=importlib.util.spec_from_file_location('deps263',k/'runtime-dependencies.py');deps=importlib.util.module_from_spec(sp);sp.loader.exec_module(deps)
host=deps.inventory();(k/'host-dependencies.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
warnings=lambda s:set(re.findall(r'^.*warning:.*$',s,re.M))
assert not warnings((k/'renderer-build001.log').read_text(errors='replace'))-warnings((parent/'renderer-build001.log').read_text(errors='replace'))
r=dict(passed=True,physical_access=False,debugger=True,guest_launched=False,ordinary_qualified=False,pixel_preservation_proved=False,
    parent_frozen_inputs=len(frozen),host_dependencies=len(host),renderer_sha256=b['executable_sha256'],
    compiled_changed_sources=b['changed_sources'],same_byte_exact_helpers=same,mask_combinations=1024,
    reused262_tests=True,all_old_refusal_predicates_retained=True,independent_launch_reply_deadline_seconds=20,
    scope='Only immutable terminal reporting of actual pending predicate mask added; no retry/clear/relaxation. Same probe/driver, scalar capacities, actual ownership/GL/pixel/callback/cold/host/event gates.')
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.json','.patch']:frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('263 frozen',len(frozen),'inputs; no guest launch')
