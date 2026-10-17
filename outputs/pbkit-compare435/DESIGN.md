# Same framebuffer before and after normal PBKit initialization

One fresh standalone 1080i boot, unchanged installed nxdk and owned allocations.
Four ten-second observations: orange bar, original parity; orange bar, shifted
parity; cyan bar, original parity after normal pb_init; cyan bar, shifted parity.
The two pairs use the same stock framebuffer pointer, physical address, pitch,
mode and pattern. pb_show_debug_screen is the supported return to that buffer.
No application GPU draw, pb_finished, manual timing/encoder/IRQ patch or borrowed
firmware commands. PBKit itself performs its broad normal graphics initialization.
Its registered shutdown callback performs normal cleanup on firmware restart.
This is NOT a one-register experiment or Windows GPU ownership.

Each phase saves a 512-byte identity/register header and the complete 1024x512
pattern before the visible pause. Independent host decoding checks every pixel,
mode/base/allocation, parity and register selector restoration. Full-frame native
checks use the same helper and are separately labeled. An append-only exclusive
journal is flushed before/after initialization and each phase. The initial
pattern remains allocated; no live mode switch or framebuffer free during PBKit.
No source patch or SDK rebuild. CRTC index writes only save/select/restore.

At 1080x1920x32 PBKit rounds its private tile pitch to 10240: three color buffers
and one depth buffer total 44,253,184 bytes after allocation alignment, plus
532,480 pushbuffer bytes, three page-rounded DMA allocations and fixed instance
memory. Require 48 MiB free AFTER the stock 8,294,400-byte framebuffer allocation.
This is a conservative total-memory preflight, not contiguous-memory assurance;
PBKit allocation failure remains a failure. We do not CPU-write PBKit tile buffers.
Debug-buffer pitch stays 7680 and is independently decoded from CRTC registers.

Application visible pauses and busy polling are finite. SDK initialization,
filesystem calls and its normal shutdown callback contain synchronous/unbounded
paths; no independent cancellation guarantee. Host observes one accepted launch,
allows a bounded return window and requests screen/reset information if it does
not return. Never retry a sent launch or silently reset/relabel a failed run.
Result output is D: CRT launch alias in a unique Xbox E application directory.
Xbox C and installed Windows/default 720p launcher remain untouched.

Visual interpretation requires user observation: clean cyan after broken orange
would implicate the changed initialization set, not prove PCRTC_CONFIG alone.
Unchanged failure narrows that comparison only, not every software or adapter
explanation. Capture bytes are pre-output CPU pixels, not emitted field evidence.
