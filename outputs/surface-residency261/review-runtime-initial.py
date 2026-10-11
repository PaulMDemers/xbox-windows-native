"""Freeze261 once, keeping parent manifests untouched and review output unique."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'surface-bridge260'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();read=lambda p:json.loads(p.read_text())
assert not (k/'runtime-review.json').exists() and not (k/'emulator-frozen.json').exists()
frozen=read(old/'emulator-frozen007.json')
for n,h in frozen.items():assert sha(ws/n)==h,n
for name in ['attestation-review001.json','probe-review001.json','callsite-review.json']:assert read(k/name)['passed']
for n,h in read(k/'attestation-review001.json')['inputs'].items():assert sha(k/n)==h,n
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():assert sha(ws/n)==h,n
probe=read(k/'probe-review001.json');assert {'VirtualLock','GetModuleHandleA'}<=set(probe['imports']['kernel32.dll'])
assert sha(k/'expected.h')==sha(k.parent/'surface-renderer259/expected.h')
assert sha(k/'attest.py')==sha(old/'attest.py') and sha(k/'atomic_json.py')==sha(old/'atomic_json.py')
assert read(old/'atomic-json-test.json')['real_windows_sharing_retry_passed']
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
for p in k.glob('*.py'):ast.parse(p.read_text())
assert "runtime-review.json" in (k/'run.py').read_text() and 'runtime-review003' not in (k/'run.py').read_text()
r=dict(passed=True,guest_launched=False,physical_access=False,debugger=True,ordinary_qualified=False,pixel_preservation_proved=False,
 parent_frozen_count=len(frozen),probe_sha256=probe['native_sha256'],header_lock_bytes=4096,
 renderer_sha256=read(old/'renderer-build001.json')['executable_sha256'],
 unchanged_driver_sha256=read(k/'build001.json')['driver_sha256'],attestation_synthetic_checks=26,
 description='Only native diagnostic probe changed: checked VirtualLock of its own PE-header page before checkpoints; all independent pixel expectations, renderer, retained arena driver, identity and ownership gates unchanged. Actual007 PTE proved header nonresident. Bounded tested atomic recorder retained.',
 source_sha256=sha(Path(__file__)))
(k/'runtime-review.json').write_text(json.dumps(r,indent=2)+'\n')
for p in k.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.json']:frozen[p.relative_to(ws).as_posix()]=sha(p)
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():frozen[n]=h
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n');print('261 fresh runtime frozen:',len(frozen),'inputs; no guest launch')
