"""Freeze one diagnostic protocol after its preparation and source review."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'runtime-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(k/'renderer-build001.json');assert build['passed'] and build['borrowed_sources_restored']
for n,h in build['inputs'].items():assert sha(k/n)==h,n
art=Path('E:/Codex-archive/xbox-windows-native/bridge260-build001')
assert sha(art/'xemu-bridge260.exe')==build['executable_sha256']
pins=read(k/'renderer-source-pins001.json')
for n in build['original_sources']:assert sha(art/'source'/n)==pins[n],n
for name in ['callback-review001.json','attestation-review002.json']:
 result=read(k/name);assert result['passed']
 for n,h in result['inputs'].items():assert sha(k/n)==h,n
for n,h in read(k/'prior-attestation001/attestation-review001.json')['inputs'].items():
 p=k/'prior-attestation001'/n
 if not p.exists():p=k/n
 assert sha(p)==h,n
for n,h in read(k/'attestation-inputs001.json')['dependencies'].items():assert sha(ws/n)==h,n
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
f=read(k/'emu001/fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
assert read(k/'emu001/before/allocation.json')['allocation_consistent']
log=(k/'renderer-build001.log').read_text();warnings=[line for line in log.splitlines() if 'warning:' in line]
parent={line.split('warning:',1)[1] for line in (k.parent/'surface-renderer259/renderer-build001.log').read_text().splitlines() if 'warning:' in line}
new=[line for line in warnings if line.split('warning:',1)[1] not in parent];assert not new,new
bridge=(k/'bridge.c').read_text();trace=(k/'trace.py').read_text()
assert 'd->worker247.state)!=0' in bridge and 'd->preserve227.state)!=0' in bridge
assert 'async_safe_run_on_cpu' in bridge and 'qatomic_load_acquire(&a->done)' in bridge
assert 'g.write(' not in trace and 'g.send(\'P' not in trace and 'pmemsave' not in trace
assert 'wait_stop(5,True)' in trace and 'remaining_breakpoints' in trace
changed=set(build['changed_sources']);assert len(changed)==5
r=dict(passed=True,physical_access=False,guest_prepared=True,guest_launched=False,
 runtime_qualified=False,pixel_preservation_proved=False,ordinary_qualified=False,native_gpu_ownership=False,
 renderer_sha256=build['executable_sha256'],source_sha256=sha(Path(__file__)),
 inherited_warnings=len(warnings),new_warnings=len(new),callback_checks=read(k/'callback-review001.json')['output'],
 complete_attestation_synthetic_checks=read(k/'attestation-review002.json')['checks'],
 projected_protocol='One launch, five native checkpoints, four monotonic renderer slots with two acknowledged CPU audits each, exact pin/handle/four-page checks, real guest read/write operations, bounded failure quarantine, cold audit',
 limitations=['Unknown enabled vertex range refuses admission','Parent Ft49 remains a strict event failure','Inherited historical emulator device policy is not current physical demo'])
dest.write_text(json.dumps(r,indent=2)+'\n')
frozen=read(k.parent/'surface-pattern258/emulator-frozen.json')
for p in k.glob('*'):
 if p.is_file() and p.suffix in ('.py','.c','.h','.ps1','.json','.patch') and p.name!='emulator-frozen.json':frozen[p.relative_to(ws).as_posix()]=sha(p)
frozen[(k/'emu001/fixture.json').relative_to(ws).as_posix()]=sha(k/'emu001/fixture.json')
(k/'emulator-frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
print('260 bounded diagnostic runtime inputs frozen; no launch yet;',len(frozen),'input pins')
