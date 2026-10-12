"""Read-only artifact audit; refuses to overwrite the closed review record."""
import hashlib,json,struct,subprocess
from pathlib import Path
from decode import decode

k=Path(__file__).resolve().parent
dest=k/'final-review.json'
assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((k/n).read_text())
build=read('renderer-build001.json');review=read('source-review.json')
assert build['passed'] and build['borrowed_sources_restored'] and review['passed']
assert build['changed_sources']==['hw/xbox/nv2a/pgraph/gl/texture.c']
assert not build['guest_launch'] and not build['gl_executed'] and not build['physical_access']
art=Path('E:/Codex-archive/xbox-windows-native/lifetime273-build001')
exe=art/'xemu-lifetime273.exe'
assert sha(exe)==build['executable_sha256']==review['executable_sha256']
assert exe.stat().st_size==build['executable_bytes']
assert sha(k/'renderer-delta001.patch')==build['delta_sha256']
for name,h in build['inputs'].items():
    assert sha(k/name)==sha(art/'inputs'/name)==h,name
pins=read('renderer-source-pins001.json')
source_files=[p for p in (art/'source').rglob('*') if p.is_file()]
for p in source_files:assert sha(p)==pins[p.relative_to(art/'source').as_posix()],p
old=(k.parent/'unit-reuse269/watch.c').read_text()
new=(k/'watch.c').read_text().replace('#include "wire.h"',
    (k/'wire.h').read_text().replace('#include "lifetime.h"',(k/'lifetime.h').read_text()))
path=Path('hw/xbox/nv2a/pgraph/gl/texture.c')
text=(art/'source'/path).read_text()
parent=Path('E:/Codex-archive/xbox-windows-native/reuse269-build005/source')
assert text.count(new)==1 and text.replace(new,old)==(parent/path).read_text()
assert (k/'lifetime.h').read_bytes()==(k.parent/'lifetime-accounting270/lifetime.h').read_bytes()
for name in build['original_sources']:
    if name!=path.as_posix():assert (art/'source'/name).read_bytes()==(parent/name).read_bytes()
verified=0
for attempt in ['002','004']:
    result=read('host-tests'+attempt+'.json');assert result['passed']
    capsule=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host'+attempt)
    for name,h in result['files'].items():assert sha(capsule/name)==h;verified+=1
for attempt in ['001','003']:
    result=read('host-tests'+attempt+'.json');assert not result['passed'] and result['compile_exit']!=0
good=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host002/terminal.bin').read_bytes()
decoded=decode(good);assert decoded['sequence']==1000006 and not decoded['full_reuse_qualified']
bad=Path('E:/Codex-archive/xbox-windows-native/lifetime273-host004/overflow.bin').read_bytes()
try:decode(bad)
except AssertionError:pass
else:raise AssertionError('Overflow qualified')
# Confirm the source-level distinction between initial owner acknowledgment and
# monitor-thread seal. These are design pins, not runtime boundary coverage.
renderer=(art/'source/hw/xbox/nv2a/pgraph/gl/renderer.c').read_text()
seal=renderer.split('if (!strcmp(value,"seal269")) {',1)[1].split('\n    }',1)[0]
assert 'pgraph_gl_reuse269_seal()' in seal and 'x260_cpu_boundary' not in seal
assert 'x260_cpu_boundary(d,v,0)' in renderer and 'x260_cpu_boundary(d,v,1)' in renderer
assert 'pgraph_gl_ledger265_worker(d)' in (art/'source/hw/xbox/nv2a/pfifo.c').read_text()
result=dict(closed=True,host_accounting_passed=True,renderer_compiled=True,
    guest_prepared=False,guest_launched=False,runtime_reuse_qualified=False,
    release_installed=False,physical_access=False,
    private_host_files_rehashed=verified,private_renderer_sources_rehashed=len(source_files),
    immutable_build_inputs_verified=len(build['inputs']),
    executable_sha256=sha(exe),actual_adapter_seal_races=4096,
    repeated_decrements=1000000,independent_wire_mutations_rejected=115,
    reserved_lifecycles_survive_overflow=True,overflow_terminal_rejected=True,
    preserved_failed_host_attempts=['001','003'],
    ordinary_texture_source_reconstructed=True,
    terminal_owner_boundary_still_required=True,
    boundary_sources={n:sha(art/'source'/n) for n in
        ['hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pfifo.c']},
    running_sessions=[])
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
