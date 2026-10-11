"""Read-only pins for the installed SDK and candidate owned workload paths."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent; sdk=Path('C:/nxdk')
sha=lambda b:hashlib.sha256(b).hexdigest()
head=subprocess.check_output(['git','-C',str(sdk),'rev-parse','HEAD'],timeout=30).decode().strip()
assert head=='58427c078b4ccb0121f359b6b6c536b3b2914976'
files=['Makefile','bin/nxdk-cc','bin/nxdk-link','lib/pbkit/pbkit.c','lib/pbkit/pbkit.h',
       'lib/pbkit/pbkit_dma.c','lib/pbkit/pbkit_dma.h','lib/pbkit/pbkit_pushbuffer.c',
       'lib/pbkit/nv_regs.h','lib/libpbkit.lib','samples/mesh/main.c','samples/mesh/Makefile',
       'samples/mesh/vs.vs.cg','samples/mesh/ps.ps.cg','samples/triangle/main.c',
       'samples/triangle/vs.vs.cg','samples/triangle/ps.ps.cg','samples/hello/main.c']
pins={name:dict(bytes=len((sdk/name).read_bytes()),sha256=sha((sdk/name).read_bytes())) for name in files}
src=Path('E:/Codex-archive/xbox-windows-native/retirement264-source001/hw/xbox/nv2a/pgraph/gl/texture.c')
oldpins=json.loads((k.parent/'backend-actors267/renderer-source-pins001.json').read_text())
assert sha(src.read_bytes())==oldpins['hw/xbox/nv2a/pgraph/gl/texture.c']
result=dict(sdk=str(sdk),head=head,pins=pins,normal_texture_source=str(src),normal_texture_sha256=sha(src.read_bytes()),
  sdk_modified=False,guest_prepared=False,guest_launched=False,physical_access=False,
  candidates=[
    dict(path='C:/nxdk/samples/mesh',use='Actual contiguous texture allocation, normal texture register setup, shader and indexed draws',
         insufficiency='Animated single-texture workload with unbounded loop; no four-unit immutable control/checkpoints/oracle'),
    dict(path='C:/nxdk/samples/triangle',use='Simpler vertex program and direct draw setup',
         insufficiency='No textured draw or lifetime discriminator'),
    dict(path='C:/Users/Paul/Desktop/ogxbox-linux/run-xemu-nxdk-color-bars.ps1',use='Existing launcher reference only',
         insufficiency='Referenced run/xemu-nxdk-color-bars.toml is absent; not a ready fixture. No launcher executed')],
  source_findings=[
    'pb_init claims instance memory and creates/binds its DMA and graphics contexts; this is standalone Xbox application initialization, NOT a safe Windows renderer retirement operation.',
    'pb_busy compares FIFO GET/PUT and PGRAPH_STATUS; it does not attest host GL/context/shader/callback ownership.',
    'pb_finished submits ASK_FOR_IDLE/NOP/interrupt then changes back-buffer index; it is not a stable framebuffer identity or full retirement acknowledgment.',
    'pb_agp_access provides linear AGP alias; any future readback must identify exact allocation/pitch/tiling and maintain framebuffer ownership.',
    'Normal xemu disabled texture path unbinds four GL targets but retains unit reference; an actual draw invoking normal binder is needed after disabling, not merely writing enable registers.',
    'Normal re-enable can take fast or slow path, dirty memory may replace cache object; independent generation/key/source/GL and final framebuffer comparisons remain required.'
  ])
dest=k/'fixture-review.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(head=head,files=len(pins),guest_launched=False,source_pin_verified=True),indent=2))
