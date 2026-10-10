# GPU transfer contract review212

The211 measured scene is dominated by explicitly bounded CopyBits uploads.
No new bounds or framebuffer-cache flag is justified by that result. A GPU
copy path must have a separate memory, ownership and completion contract.

Actual compiled210 surface.c allocates ShadowBits with EngAllocMem using only
FL_ZERO_MEMORY. EngLockSurface supplies bitmap access; it does not turn these
pages into a device DMA allocation. The [EngAllocMem contract](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engallocmem)
describes the paged/nonpaged flag. Neither a virtual bitmap address nor a masked
Xbox-kernel pointer is accepted as a transfer capability here.

binary-inventory.json pins captured NT5 kernel/GDI/video-port binaries and exact
bounded disk-entry windows. abi-review.json additionally follows bounded entry
control flow to all direct returns, recording imported calls without decoding
their entire implementations. Actual stack cleanup is32bytes for
MmAllocateContiguousMemorySpecifyCache,12for its matching free,4for physical
translation,16for VideoPortAllocateContiguousMemory,24for each old common-buffer
function and28for EngDeviceIoControl. This is on-disk evidence, not execution.

The captured NT5 video port exports VideoPortGetCommonBuffer/FreeCommonBuffer
and AllocateContiguousMemory, but not the XP-era AllocateCommonBuffer API. Its
actual two allocation entry paths reject lengths above0x40000. GetCommonBuffer
also rejects an absent initialized adapter. No claim is made that the current
miniport has such an adapter. The [modern common-buffer API](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/video/nf-video-videoportallocatecommonbuffer)
lists XP as its minimum; substituting that API would not resolve NT5 ABI support.

The selected precursor uses a16KiB owned allocation through the actual kernel's
MmAllocateContiguousMemorySpecifyCache, with explicit physical bounds excluding
the firmware's top4MiB. Its free retains exact size/cache arguments. The
[allocation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmallocatecontiguousmemoryspecifycache)
and [free](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmfreecontiguousmemoryspecifycache)
contracts support this CPU-only lifetime. Per-page MmGetPhysicalAddress checks
test translation consistency only. Microsoft explicitly distinguishes that
[translation API](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-mmgetphysicaladdress)
from device DMA addressing. A successful213 probe does not resolve bus address,
cache visibility, device mapping, or a GPU DMA contract.

The captured HAL supplies KeGetCurrentIrql. Absence of KeMemoryBarrier or
KeFlushIoBuffers as exports is not proof that no macro/intrinsic implementation
exists. MmClaimGpuInstanceMemory is absent from the inventoried NT5 kernel/HAL;
the nxdk Xbox-kernel Ex/claim APIs cannot be copied into this driver by renaming.

The current miniport has no FIFO/context initialization, hardware interrupt
handler, submission queue or completion/drain implementation. Reset merely
returns TRUE. Shared0106 acquisition retains the permanent UC crash view and
checks display ownership; its reference is not a render/GPU fence.

Pinned nxdk58427c07 pbkit.c is a useful MIT-licensed source reference. pb_init
allocates special GPU instance memory, programs RAMHT/RAMFC/context objects,
installs an interrupt handler, changes timer/interrupt/global configuration,
uses wbinvd and allocates/changes scanout buffers. pb_kill contains unbounded
busy/swap waits and proceeds beyond a DMA wait warning to free allocations.
Those assumptions do not implement this NT5 timeout/crash contract. This is a
porting limitation, not a statement about pbkit's validity in its own environment.
No pbkit initializer, global reset, cache flush or cleanup was executed.

Before any GPU submit:

1. Identify firmware/NT5 GPU state and instance-memory ownership. PRAMIN and
   context storage must not overlap shared0106's visible/hidden boot buffers or
   unreserved NT pages. An idle status is not proof that another owner is absent.
2. Establish an NT5-supported device address/lifetime/cache contract for command,
   source and disjoint destination allocations. Keep addresses private to the
   miniport; accept bounded counted pixels/rectangles, not arbitrary pointers.
3. Reserve a single transfer queue/context and resident completion observation.
   Match completion to the submitted sequence; reject incomplete/faulted work.
4. Begin with a guarded disjoint16x8 destination, independent CPU bitmap and raw
   bytes. Do not write scanout, change modes or invoke a full pbkit application.
5. Drain before freeing, fallback, reset, PnP/ownership change or crash rendering.
   Timeout cannot release a referenced buffer or start conflicting CPU writes.
   If a bounded hardware stop cannot be proved, quarantine the resident
   allocations and leave acceleration unavailable until reset/reboot.

transfer_plan.h is pure bounded staging geometry, with no addresses, allocation
or GPU authority. It validates complete source/destination layouts, explicit
rectangles and at most64KiB packed strips, including different pitches. It does
not clip malformed requests, program a GPU, or establish ordering.324 independent
pixel/guard cases and100000 malformed plans pass each of two ASan/UBSan builds;
host-tests001.json retains exact source/binary pins and8,923,567 checks per run.
These are host-only checks.1920x1080 exceeds the retained4MiB layout limit and is
rejected; this is not a new-mode capability.

source-inventory001-failure.json preserves the first read-only wrong-header-path
attempt and partial private copies. Corrected002 preflights and pins13 actual
source/header files. Individual hashes remain authoritative alongside the tree.
Original physical0101/video0093,0088 rollback and immutable0.1.0 are unchanged.

The pinned boot provider reserves316160 indexed backbuffer bytes at the top of
its4MiB reservation. On a64MiB machine that is03fb2d00..04000000. The commented
pbkit instance pointer03feb000..03ff0000 would overlap all20480 bytes of that
example range. This is conditional source arithmetic: the pointer has no later
uses in the pinned pbkit source, and actual firmware PRAMIN placement/claim
results were not observed. It is not evidence of a physical collision.

ramin-model.json pins the actual685f24e3 xemu build's compiled nv2a.c manifest,
including the existing resource-model patch. nv2a_init_memory creates a separate
1MiB RAMIN RAM region; its suggested alias into VRAM is commented out. That
resource patch adds a BAR2 alias to RAMIN, not physical shared-RAM backing.
Consequently even an eventual guarded GPU-copy emulator pass cannot establish
physical instance-memory ownership or non-overlap. No model was changed here.
The first model inventory compared restored original source against a patched
manifest; the second passed a multi-file patch to one explicit file and rejected
the header part. Both failed scripts/partial copies are retained.003 reconstructs
only the NV2A section privately and matches its full compiled-source hash.
