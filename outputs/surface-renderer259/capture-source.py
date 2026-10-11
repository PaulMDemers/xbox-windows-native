"""Read-only exact257 source closure for the pending renderer/CPU collector."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
assert sys.platform=='linux';dest=k/'source-review001.json';assert not dest.exists()
prior=k.parent/'surface-invalidation257';pins=json.loads((prior/'candidate002-source-pins.json').read_text())
tree=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
capsule=prior/'artifacts/build002/source';out=k/'source';out.mkdir(exist_ok=False)
names=['hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.c',
 'hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/vertex.c',
 'hw/xbox/nv2a/pgraph/gl/texture.c','hw/xbox/nv2a/pgraph/gl/reports.c',
 'hw/xbox/nv2a/pgraph/gl/display.c','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/common.c',
 'hw/xbox/nv2a/pgraph/surface.h','hw/xbox/nv2a/pgraph/pgraph.h',
 'hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pfifo.c',
 'system/physmem.c','include/hw/core/cpu.h','cpu-common.c']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,guest_launch=False,borrowed_sources_modified=False,files={})
try:
 for name in names:
    source=capsule/name
    if not source.is_file():source=tree/name
    assert name in pins and sha(source)==pins[name],name
    target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
    r['files'][name]=dict(sha256=sha(target),bytes=target.stat().st_size,source=str(source))
 r['passed']=True
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print('259 exact257 source closure copied:',len(r['files']))
