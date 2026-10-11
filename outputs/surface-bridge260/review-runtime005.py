"""Freeze fresh003 against closed002 inputs and the actual IDT symbol source."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (k/'emulator-frozen005.json').exists()
frozen=read(k/'emulator-frozen004.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
for n,h in read(k/'kernel-discovery-review.json')['inputs'].items():assert sha(k/n)==h,n
pub=ws/read(k/'kernel-discovery-review.json')['symbol_source'];assert sha(pub)==read(k/'kernel-discovery-review.json')['symbol_sha256']
f=read(k/'emu005/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert read(k/'emu005/before/allocation.json')['allocation_consistent']
for name in ['trace005.py','run005.py','audit005.py','typed-state005.py']:ast.parse((k/name).read_text())
trace=(k/'trace005.py').read_text()
assert "discovery.discover(observed_read" in trace and "inspector.pin('ntoskrnl.exe',kernel,rva,16)" in trace
assert 'row[\'partial_pins\']=inspector.pins.copy();save()' in trace
assert "# Diagnose only the failing mapping" in trace and 'g.write(' not in trace
assert not (k/'emu005/runner-start.json').exists()
r=dict(passed=True,guest_launched=False,debugger=True,physical_access=False,ordinary_qualified=False,pixel_preservation_proved=False,
 immutable_parent_inputs_verified=len(frozen),kernel_discovery_synthetic_checks=10,attestation_synthetic_checks=26,
 renderer_unchanged=read(k/'renderer-build001.json')['executable_sha256'],
 description='Correct HMP JSON flag -j, with live rejected-before-admission parser controls; Actual IDTR vectors0/14 derive kernel base, PE and both resident trap entries pinned, then unchanged full native ownership checks. Every requested read/error and partial pins persisted. Failed virtual access diagnoses page tables only, no dirty payload read or fallback guess.',
 inputs={n:sha(k/n) for n in ['review-runtime005.py','trace005.py','run005.py','Run005.ps1','audit005.py','typed-state005.py','kernel-discovery.py']})
(k/'runtime-review003.json').write_text(json.dumps(r,indent=2)+'\n')
for n in list(r['inputs'])+['runtime-review003.json','kernel-discovery-review.json','emu005/fixture.json']:
 frozen[(k/n).relative_to(ws).as_posix()]=sha(k/n)
frozen[pub.relative_to(ws).as_posix()]=sha(pub)
(k/'emulator-frozen005.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('003 prelaunch review PASS;',len(frozen),'frozen inputs')
