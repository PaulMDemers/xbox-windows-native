# Owned direct-RAM framebuffer mapping

Candidate0096 follows the preserved0095 rejection: VideoPortMapMemory returned
ERROR_INVALID_PARAMETER for the direct RAM address. It uses MmMapIoSpace with
MmNonCached for the loader-reserved top4MiB instead. Bootvid already maps this
RAM that way. Geometry, GPU scanout, display mode and storage drivers stay fixed.

The mapping helper is owned by this single-GPU miniport. A fast mutex protects
owner/base/address/reference state. Only null requested virtual addresses and
64/128MiB reserved bases are accepted at PASSIVE_LEVEL. Repeated same-owner
maps share a reference; invalid-owner/address unmaps are rejected. Final unmap
releases all4MiB. The existing unload wrapper releases any remaining mapping
AFTER VideoPort's original unload callback. No user mapping or mode switch is
supported. No direct CPU cache-register or page-table modification is added;
normal OS mapping APIs own the PTE updates. Hot removal/re-enumeration is not
qualified by this experiment.

Source tree: eded91e06d6cac60a1cf66bc8a05117ebfa6a71a.
Miniport SHA256: e8021879bd606eb9cfc6927fbf50565c41781779af86e56f4678fa890b6eb6ec.
Reconstruction pins are in inputs.json/manifest.json. Both direct-RAM and owned
mapping build switches default OFF; this experiment enables them. The owned
mapping option requires the existing trace/unload wrapper.

Compiled execution tests cover imports, geometry, map failure, request/output
ABI, reference reuse, wrong owners/pointers, elevated IRQL, double unmap and
unload cleanup under modeled mutexes. This does not prove live concurrency or
NT5 mapping behavior. The live trace must show actual first/last RAM PTEs with
UC cache type; cold GDI/payload/event/shutdown checks must also pass before a
single bounded physical run. Collect and restore0093 afterward; remote backup
xboxvnt5.trace014. Mode remains1024x576x32; FATX0088 is unchanged.

A first physical performance sample will be exploratory, not a release or a
window-drag FPS measurement. Check reports for actual results. Retain failed
0095 and0094's physical strict failure due to shutdown popups.

## First emulator result

The ordinary boot reached the desktop and passed all four GDI pixel checks,
normal restart and unchanged payload checks. Actual PTEs confirm direct RAM
0x03C00000..0x03FFFFFF and UC cache type. Strict audit is FALSE because two
rundll32 DLL-initialization popups occurred at shutdown. No physical0096
deployment was made from this result. A separately identified120-second
settling protocol is in ../video-direct-map-settled; the driver is unchanged.

## API constraints checked

[Microsoft MmMapIoSpace](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmapiospace)
and [MmUnmapIoSpace](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmunmapiospace)
permit calls up to DISPATCH_LEVEL. The helper only accepts PASSIVE_LEVEL entry;
[fast mutexes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/fast-mutexes-and-guarded-mutexes)
raise it to APC_LEVEL inside the protected mapping operation. This RAM must
remain reserved from the memory manager for the complete mapping lifetime; it
is not an arbitrary pageable RAM mapping. The pinned loader's4MiB reservation
is a prerequisite, not something the helper can create by mapping the address.

Production lifecycle work remains: generic PnP stop/removal must release mappings
after consumers are quiesced, including asynchronous completion and restart.
The current experiment covers normal display unmap and driver unload, not all
stop/remove transitions. Do not promote this bounded prototype as a general
replacement until that lifecycle is implemented and exercised. A physical
measurement can determine whether pursuing this access path is worthwhile.
