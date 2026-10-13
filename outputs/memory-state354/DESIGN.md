# Read-only current memory-state discriminator

353 proved that the direct-copy path was exercised and did not materially improve
physical timing.354 observes the actual private shadow and scanout page policies;
it does not change mappings or attempt another copy optimization.

Installed lineage is deliberately split: display303 (b23b94ac...) obtains the
mapping through miniport300 (74ccdc9f...) and bootvid300 (0c8f5d49...). The latter
publishes the permanent nine-MiB direct-RAM mapping requested as MmNonCached.
The351 experimental display tree contains older, unrelated bootvid files; those
are not evidence of the installed provider. source-review001.json pins the actual
300 source, flags and matching last353 installed hashes. ShadowBits is allocated
with EngAllocMem(FL_ZERO_MEMORY). Neither API choice proves effective cache type.
The old0094 physical capture concerned the obsolete GPU-aperture mapping only.

New exact351 child adds escape0x5857443a with no input, fixed66560-byte output.
Existing identity, ownership lookup, GDI surface/PDEV lifetime, drawing, upload,
primary-copy accounting and teardown are unchanged. The driver snapshots only
its registered PDEV's shadow and scanout, never caller-supplied addresses. It
checks bounded positive32bpp geometry, nonoverlapping virtual ranges, Intel
family6/model8, advertised MSR/PAT/MTRR support and non-PAE paging. It reads CR0,
CR3, CR4, CPUID, PAT, MTRRCAP, default/variable/fixed MTRRs. Unsupported CPUs,
too many variable ranges, missing or large/user pages and read faults refuse.

The pinned NT5 recursive PDE must match CR3 before any buffer page walk. Every
covered page is recorded in order, with capacity4096. All translations are read
again, ignoring only naturally changing accessed/dirty bits; CPU/MSR snapshots
and owner/geometry are checked again. Fault handling preserves an error packet.
This is not an atomic MM snapshot: equal observations cannot exclude intervening
ABA, stale TLB entries, inactive/future aliases or another processor. It is not
permission to change memory type. No CR/MSR/PTE/cache writes, invalidations,
interrupt masking, new physical aliases, GPU ownership, or functional copy changes.

The independent decoder validates the complete fixed envelope, row order and
coverage, CPU state, reserved fields, MTRR masks/overlaps/fixed priority, PAT and
Intel effective-type combination. Unsupported global caching modes refuse rather
than being guessed as UC. Runtime qualification additionally joins every scanout
page to the actual retail64 reservation at55MiB and requires shadow pages below
it. Capture before/after each normal graphics sample; preserve a refused packet
without retry. All graphics/audio/shutdown/cold/event gates remain required.

Current control measures no new throughput. Once actual hardware state is known,
the next distinct discriminator may measure bounded independent owned RAM copies
against existing upload timing. It must retain source/guard checks and distinguish
elapsed/preempted time from CPU cycles. Do not infer cache type from timing, or
silently promote a cache-state sample to a complete alias/lifetime proof.

References: [Intel253668-021, sections10.11/10.12 and table10-7](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366821.pdf)
and [Microsoft EngAllocMem](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engallocmem).
