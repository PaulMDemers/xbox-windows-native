# Transfer contracts212

The measured211 movement uploads justify a transfer investigation: CopyBits
accounts for57,344,000 of66,738,880 phase bytes. They do not establish frame rate
or a general bottleneck.212 identifies the contracts required before submission
and implements a bounded staging planner; no GPU commands or physical changes
were made.

Actual captured NT5 binaries and preserved compiled headers/source establish the
allocation ABI. Existing VideoPort common-buffer/contiguous paths cap a request
at256KiB; common-buffer use also requires an initialized adapter. The newer
VideoPortAllocateCommonBuffer API is absent. The actual kernel exports the
reviewed contiguous allocator, matching free and address-translation functions.
Entry CFG/stack-cleanup analysis is on-disk evidence, not resident execution.
The213 companion runs exercise the real CPU allocation/copy/free path separately.

ShadowBits currently comes from EngAllocMem without FL_NONPAGED_MEMORY. Neither
EngLockSurface nor a translated physical address establishes a DMA contract.
The miniport has no implemented queue, context setup, completion interrupt or
drain. The shared UC crash framebuffer remains unchanged. See the actual
inventories and DESIGN.md for ownership, timeout quarantine and crash obligations.
The API distinction follows the primary [EngAllocMem documentation](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engallocmem)
and [MmGetPhysicalAddress documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-mmgetphysicaladdress).

The pure planner passed324 independent pixel/guard cases,1306 strips and100000
malformed descriptors at both O0/O2 with ASan/UBSan:8,923,567 checks each.
It bounds complete layouts, explicit rectangles, differing pitches and≤64KiB
strips, with64-bit extent intermediates and zeroed failures. It grants no GPU
authority.1920x1080 is rejected by the4MiB layout cap; no video mode was added.

Pinned nxdk pbkit is a source reference, not an NT5 initializer. Its Xbox-kernel
APIs, global GPU/cache/interrupt changes and unbounded cleanup cannot be copied
as this driver's lifetime contract. A commented20KiB placement overlaps the
actual bootvid backbuffer reservation by arithmetic, but no actual PRAMIN alias
or physical collision has been proved. The exact compiled xemu source gives
RAMIN separate backing RAM, so it cannot prove physical non-overlap either.

All failed inventory attempts remain visible: wrong header path, original-versus-
patched model hash mismatch, and multi-file patch applied to one file. Corrected
inventories preserve full source copies privately and exact identities in reports.
Physical0101/video0093,0088 rollback and0.1.0 remain unchanged. No acceleration,
new mode, physical qualification or release promotion is claimed.
