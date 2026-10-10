"""Freeze and patch an isolated boot provider; never edit its parent or launch."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts/source'
assert not art.exists() and not (k/'source-review.json').exists()
base=ws/'outputs/video-gpu-transfer-contract212/artifacts/boot-reservation'
record=json.loads((ws/'outputs/video-gpu-transfer-contract212/boot-reservation.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
for n,digest in record['source_pins'].items():
    p=base/n;assert sha(p)==digest
    q=art/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);pins[n]=digest
path=art/'drivers/base/bootvid/i386/xbox/bootvid.c';old=path.read_text();text=old
def replace(a,b):
    global text
    assert text.count(a)==1,a;text=text.replace(a,b)
replace('#include "precomp.h"','#include "precomp.h"\n#include "boot_layout.h"')
replace('static PUCHAR BackBuffer = NULL;','static PUCHAR BackBuffer = NULL;\nstatic ULONG BootWritableBytes;')
start=text.index('    /* Verify that screen fits framebuffer size */')
end=text.index('    /* Return the address back to GPU memory mapped I/O */',start)
text=text[:start]+'''    ULONG BackBufferSize = SCREEN_WIDTH * (SCREEN_HEIGHT + BOOTCHAR_HEIGHT + 1);
    XWN_BOOT_LAYOUT Layout;
    if (!XwnBootLayout(FrameBuffer, FrameBufferWidth, FrameBufferHeight,
                       BackBufferSize, &Layout))
    {
        DPRINT1("Framebuffer intersects protected GPU tail or indexed backing!\\n");
        goto cleanup;
    }
    ULONG FrameBufferSize = Layout.VisibleBytes;

'''+text[end:]
replace('BackBuffer = (PUCHAR)(FrameBufferStart + NV2A_VIDEO_MEMORY_SIZE - BackBufferSize);',
        'BackBuffer = (PUCHAR)(FrameBufferStart + Layout.HiddenOffset);\n    BootWritableBytes = Layout.WritableBytes;')
replace('NV2A_VIDEO_MEMORY_SIZE - BackBufferSize, MmNonCached};','Layout.HiddenOffset, MmNonCached};')
replace('FrameBufferStart = 0; BackBuffer = NULL; Result = FALSE;',
        'FrameBufferStart = 0; BackBuffer = NULL; BootWritableBytes = 0; Result = FALSE;')
replace('RtlZeroMemory((PULONG)FrameBufferStart, NV2A_VIDEO_MEMORY_SIZE);',
        'RtlZeroMemory((PULONG)FrameBufferStart, BootWritableBytes);')
path.write_text(text)
q=path.parent/'boot_layout.h';shutil.copyfile(k/'boot_layout.h',q)
# A conservative relative carve-out is used for128MiB too; it grants no GPU
# capability and does not assert that the64MiB physical transform applies there.
out=dict(passed=True,parent_source_pins=pins,candidate_bootvid_sha256=sha(path),
    candidate_layout_sha256=sha(q),authoring_sha256=sha(Path(__file__)),
    physical_result_source_sha256=sha(ws/'outputs/video-instance-correlation218/physical64-analysis.json'),
    protected_tail=0x15000,writable_bytes=0x3eb000,indexed_bytes=316160,hidden_offset=0x39dd00,
    profile128='Conservative identical relative tail exclusion; physical UMA mapping unqualified.',
    parent_unchanged=all(sha(base/n)==h for n,h in pins.items()),
    mapped_bytes_unchanged=0x400000,shared_abi_changed=False,guest_launch=False,physical_access=False,
    limits='Isolated source change only. No runtime guard, GPU authority, ordinary reboot or physical driver qualification.')
assert out['parent_unchanged'];(k/'source-review.json').write_text(json.dumps(out,indent=2)+'\n')
print('Isolated boot layout authored; original provider unchanged')
