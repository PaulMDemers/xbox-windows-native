# Source review for704 (host-only)

The retained Cromwell source is pinned in sources001.json and700's manifest.
`gpu_legacy.c`, types,698 transport,685 delay and681 table are exact copies.
The authored encoder wrapper retains700's two reads, two reset writes and144
table writes/delays. Its former fixed55MiB Windows-layout check is replaced by
the transaction's checked owned-allocation contract. It is not bypassed with
fabricated framebuffer values. Physical SMC cable byte1 differs from the old
AV_HDTV enum3; request704 explicitly uses the former.

## Register handling

The Cromwell Xcalibur HDTV path supplies720x480,2880-byte stride,779/524 totals,
738/489 sync starts, common PRAMDAC setup, six CRTC setup bytes, VGA sequence,
graphics/attribute values and ACPI80d3/80d6/80d8 requests. The final CRTC19 is30
after common setup plus pitch, rather than702's inherited-low-bits result.
CR39 is explicitlyff. All changed geometry fields and retained field masks
are checked. CR11 timing bits remain inherited; this is a constrained transition,
not a from-reset driver or proof that those bits are irrelevant in TV mode.

[Linux v6.12 nouveau hw.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/hw.h)
supports checking CR11 protection, CR21 shadow access and resetting the attribute
flip-flop before indexed access. The candidate refuses a protected base, retains
CR21 and requires its documented unlock mask. It uses per-access flip-flop reset
and palette-address-source bit5. It never writes CR11: legacy interrupt-control
side effects on NV2A remain unqualified. Extended CR1f57 follows Cromwell;
success is checked through changed registers, not by assuming the readback is57.

[Linux nvreg.h](https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/dispnv04/nvreg.h)
corroborates indexed access offsets and PCRTC_START600800. The legacy helper's
incorrect600000+8000/PMC+8000 stores and interrupt status/enable writes are omitted.
No pending-bit clearing, PFB configuration write or clock programming is imported.

Raw-source downloads returned429 (sources001.json); the versioned GitHub page
was readable. These are reviewed sources, not claimed locally pinned downloads.
The actual compiled legacy inputs are independently hash-pinned local sources.

## Admission and output limits

Requires64MiB, checked contiguous720p allocation >=3686400 bytes, expected GPU
mapping and physical framebuffer pointer, IF clear, known inherited TV clock
selection,480p capability, cable1 and confirmed3375000Hz timer. It rejects703's
smaller640x480 buffer. Caller fields are obligations; they do not prove allocation,
PCI/controller identity, exclusive ownership, paging or cache state themselves.
Native payload integration must establish those independently before entry.

Clock/PFB/PCRTC-config values are read-only preconditions taken from701/703
observations, not copied firmware programming. CR21, CR44, CR11 and retained
CRTC masks have not yet been captured/qualified on this native physical path.
The eventual kernel recorder must persist these and native code must recheck.

Sequencer blanking is read back. ACPI writes have no claimed physical readback;
the models prove request order only. Any post-blank failure makes a bounded
reblank request and returns its status; the future bridge must hold without
kernel calls/retries. An output-enable failure also reblanks. If a blank write
itself fails, no blanked-screen guarantee is made. Encoder success means the
checked transport/delays completed, not independent verification of144 internal
encoder registers. The extra final500us is a bounded guard interval, not a
measured minimum physical lock time.

## Native packaging decision

Build001 wrongly required a kernel high framebuffer alias; build002 corrects
that for the paging-off bridge. Build003 additionally removes CR11 writes.
Build004 adds ELF relocation metadata and produces the identical9916-byte blob.
49 internal relocations are reviewed:26 absolute32 are rebased;23 PC-relative32
remain unchanged. Foreign symbols, unsupported types and overlaps are rejected.

The9916-byte blob cannot fit the earlier4096-byte checkpoint. A proposed32KiB
allocation reserves entry/tables in its first4KiB, <=16KiB for the transaction,
then request/result and a separate stack. Four modeled placements pass; this
does not establish the kernel allocator, low virtual aliases or paging transition.
Those are the next distinct validation step, before any XBE/console launch.
