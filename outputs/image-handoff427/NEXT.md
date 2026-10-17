# Next: read-only raw image discovery and loader projection

427 is closed host/source/static work. No new guest/build/native patch. Do not
rerun static001/002, tests001, source-review001 or review001; all earlier closed
guests remain closed. Preserve static001 age-check failure and static002 correction.

Read DESIGN.md, source-review001.json, kernel-calls002.json and tests001.json.
The selected initial route is now a CONTIGUOUS fixed image, exposed by matching
FreeLoader/HAL partition1 projection. Generic fragmented mapping426 is not this
native route. Fragmentation must fail, never be silently flattened or relocated.

1. Implement a bounded read-only FATX path/chain/full-owner verifier against exact
   recorded disk geometry. Use short path components, reject loops/crosslinks/
   incomplete owners, enforce EOF/contiguity and parent data-region bounds. Match
   experimental wrapper identity plus inner NTFS boot geometry/serial. Review
   actual total-sector and HiddenSectors semantics before fixing comparisons.
   Do not use a synthetic ownership boolean as runtime authorization.
2. Test malformed metadata/short reads/capacity/identity independently and use
   a NEW disposable fixture for actual file versus raw sector read comparison.
   No executed runtime parent. Preserve full outside-image/outside-E checks.
3. Build an opt-in loader-only partition1 projection on a private exact source
   child; read selected NTFS files and halt before kernel entry. Retain normal
   loader behavior and disk signature/checksum. No new virtual disk needed for
   the contiguous case. Inspect capacity first: C was below20GiB in427.
4. Only after loader proof implement separate HAL validation/projection at
   HalpXboxIoReadPartitionTable. Phase0 only installs hooks/captures selected mode;
   no speculative disk IO there. Independently validate before publishing layout.
   No late geometry switch or fallback to parent E. Trace actual ARC/SystemRoot/
   mount identity/exclusion before writable NTFS boot. Parent E raw writes remain
   outside what a synthesized partition table alone can prevent.

Fresh registry C mapping must use inner offset, not405's outer5633024*512.
ArcHalDeviceName needs explicit handling too. No current demo registry edits.
Keep dump settings and all strict gates; ordinary crypto/COM+/namespace/paging/
crash-recovery/install/restore qualification remains separate. No physical test
queued. All private code/disassembly/media stay private; original code is MIT,
upstream loader/HAL retain their licenses. Preserve all failed evidence/rollbacks.
