"""Exclusive262 pre-execution closure; no historical records modified."""
import ast,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'surface-residency261'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();read=lambda p:json.loads(p.read_text())
assert not (k/'runtime-review002.json').exists() and not (k/'emulator-frozen002.json').exists()
frozen=read(k/'emulator-frozen.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
b=read(k/'renderer-build001.json');assert b['passed'] and b['borrowed_sources_restored']
assert b['changed_sources']==['hw/xbox/nv2a/pgraph/gl/surface.c']
exe=Path('E:/Codex-archive/xbox-windows-native/coverage262-build001/xemu-coverage262.exe');assert sha(exe)==b['executable_sha256']
for name in ['counter-tests.json','proof-tests.json','close-tests.json']:assert read(k/name)['passed']
for name in ['attest.py','kernel-discovery.py','atomic_json.py','attestation-inputs001.json']:assert (k/name).read_bytes()==(parent/name).read_bytes()
f=read(k/'emu002/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert read(k/'emu002/before/allocation.json')['allocation_consistent']
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():assert sha(ws/n)==h,n
for p in k.glob('*.py'):ast.parse(p.read_text())
sp=importlib.util.spec_from_file_location('deps262',k/'runtime-dependencies002.py');deps=importlib.util.module_from_spec(sp);sp.loader.exec_module(deps)
host=deps.inventory();(k/'host-dependencies002.json').write_text(json.dumps(dict(files=host,physical_access=False),indent=2)+'\n')
# Only telemetry changed in the compiled source closure; source-led flags retain
# upload intent. No dirty/download/eviction bits are permitted at write retirement.
oldpins=read(k.parent/'surface-bridge260/renderer-source-pins001.json');pins=read(k/'renderer-source-pins001.json')
assert pins.keys()==oldpins.keys() and [n for n in pins if pins[n]!=oldpins[n]]==['hw/xbox/nv2a/pgraph/gl/surface.c']
oldlog=(k.parent/'surface-bridge260/renderer-build001.log').read_text(errors='replace');log=(k/'renderer-build001.log').read_text(errors='replace')
warnings=lambda s:set(re.findall(r'^.*warning:.*$',s,re.M))
assert not warnings(log)-warnings(oldlog),'New compiler warning'
r=dict(independent_launch_reply_deadline_seconds=20,never_retry_launch=True,passed=True,physical_access=False,debugger=True,guest_launched=False,ordinary_qualified=False,pixel_preservation_proved=False,
    parent_frozen_inputs=len(frozen),host_dependency_count=len(host),renderer_sha256=b['executable_sha256'],
    unchanged_probe_sha256=read(parent/'probe-review001.json')['native_sha256'],unchanged_driver_sha256=read(parent/'build001.json')['driver_sha256'],
    exact_compiled_changed_sources=b['changed_sources'],new_warning_lines=[],limits={'11':4096,'other':256},
    scope='Bounded telemetry and host closure only; identical261 guest/probe/driver/oracle, current native and GL gates retained. Old261 truncation/host failure remain failed.',source_sha256=sha(Path(__file__)))
(k/'runtime-review002.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
    if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.json','.patch']:frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu002/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu002/fixture.json')
(k/'emulator-frozen002.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('262 frozen',len(frozen),'workspace inputs and',len(host),'explicit host dependencies; no guest launch')
