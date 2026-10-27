# 730: CR22/CR33 source and unchanged setup-predicate review

Host-only review completed 2026-10-27. No XBE, console connection, new hardware
observation, hook, driver modification or old runtime reuse. Console last observed
at UnleashX after729. Windows/native modesetting on1.6 remains unqualified.

## Finding

Original704 phase4 writes11 MMIO values, then CR14/17/19/1b/22/33. Its
`check_setup` requires full equality, including CR22=ff and CR33=11. Failure
reblanks and returns T704_SETUP; the native bridge can therefore hold black after
a validation rejection. Neither708 nor709 recorded the rejecting register or
phase. The CR1b cleanup investigations do not establish that original failure.

CR22's full-byte writable-storage assumption is unsupported by the reviewed
sources. [Envytools' pinned NVIDIA VGA register definitions](https://github.com/envytools/envytools/blob/f102b82381f3f11cee113d16374c87091db039d9/rnndb/display/nv_vga.xml#L261)
name CR22 MEM_LATCH. This is a reverse-engineered register database, not an
NV2A vendor access specification; the entry does not declare read-only access.
[Bochs' pinned VGA implementation](https://github.com/bochs-emu/Bochs/blob/67980ad8f2775e80e6913d4f94b2e85fa4fe701f/bochs/iodev/display/vgacore.cc#L747)
reads the selected graphics latch for CR22 and ignores extended CRTC writes.
That generic VGA behavior is corroboration for a hypothesis, not proof of NV2A
write effects, latch selection or a safe write/restore procedure.

[Linux v6.12 Nouveau nvreg.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/nvreg.h#L265)
identifies CR33 as LCD selection/routing and defines a routing mask3b.
[Its CRTC save path](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/crtc.c#L687)
carries the saved CR33 value into mode state. This does not establish the full
NV2A writable mask, authorize replaying captured firmware programming, or prove
that writing11 causes the original failure. CR33 is not an unqualified scratch
register. No unknown bits are reclassified as pending flags or cleared.

Four retained, independently hash-checked physical snapshots show CR22=fe and
CR33=11:722's720p ->720x480p ->720p and729's720p preparation. These were working
kernel-created modes, not704 phase4 post-write measurements. They corroborate
that ff is not a universal requirement for a visible mode. FE must not become
a hard-coded replacement expectation or guessed mask.

## Fresh compiled evidence

`build001.json` records a fresh GCC12 build from unchanged, pinned704 source.
Its native.bin is byte-identical to704build004 (SHA256
126594c9ae628e7920667339aaf5963fe86984816749c03085424a98370f125c).
No old executable, fixture, VM, disk or runtime state was reused. This kit has
no console launcher and no packaged XBE.

`model001.json` contains12 fresh isolated executions of these exact instructions.
Successful cases stop at entry to phase5, before geometry, encoder, drawing or
output enable. Rejections execute the original reblank/selector restoration and
return phase4/error8. The harness permits only the original prefix's data writes
and gate5 requests; result/input/code bounds and failure selector restoration
are checked. These are hypothetical access models, not physical-register models
qualified against the Xbox.

- Ordinary writable storage passes the setup check.
- Independent CR22 readouts00/05/85/fe reject; ff passes even with its write ignored.
- An ignored CR33 write passes if the readout was already11, but00 rejects.
- CR1b85 short-circuits before CR22 is read; an earlier MMIO mismatch short-circuits
  before the CRTC checks. CR22 rejection also prevents checking CR33.
- CR22ff cannot hide a later CR33 rejection.

The earlier704 host harness stores indexed CRTC writes in a byte bank and reads
them back, including CR22. Its prior PASS remains valid for that model and is
not hardware access-semantics evidence. No earlier PASS or failure is erased.

## Limits and state

This review does not prove that CR22 readsfe after704's write, that the write is
ignored on NV2A, or that CR22 caused708/709. It changes no gate or functional code.
The downloaded primary-source files remain private, with public URL/hash/commit
pins in references001.json. Initial browser429 responses and one guessed404 path
are recorded; later bounded direct downloads succeeded. Shell search/path misses
were exploratory only, with no candidate or runtime mutation.

Build,12 compiled cases and offline source/capture audit passed without candidate
failures. Build/emulator leases released; no owned process/VM, hook or launch.
Preserve protected720p and all closed records. See NEXT.md for the evidence still
needed before another write test.
