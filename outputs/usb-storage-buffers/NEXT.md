# Next storage investigation

The first twelve payload writes have correct source, mapped and MDL data and
successful child completions; the final payload is correct. Do not patch FATX,
ATA or XID based on this passing subsection. Preserve the original failed disks
and both current outcomes.

1. Design a bounded host-side byte/hash capture at the actual IDE DMA
   scatter/gather and block-backend submission/completion boundaries. Verify the
   exact pinned emulator source and account for asynchronous buffer ownership,
   write identity and lifetime. Host entry logs do not provide this evidence.
2. Include the retained failing exit sector and registry write ranges as well as
   all five payload sectors. Capture before/after bytes, status, request identity
   and completion length. Cross the first 512-byte boundary; twelve payload
   writes were insufficient. Keep guest/storage binaries pinned and declare any
   emulator instrumentation change explicitly.
3. Use a fresh uniquely named sibling from the same closed first-boot parent,
   with cooperative leases and one launch. Retain the held setup guard and any
   host-stop limitation; do not silently complete unidentified setup dialogs.
4. Compare captured bytes with preserved cold sectors and fully traverse all
   five hives. Report empty event deltas, partial mappings and failed parsers as
   their actual scope. A timing-sensitive diagnostic cannot qualify normal boot
   or physical hardware.

The remaining distinction is whether wrong bytes reach DMA/backend submission,
correct bytes fail to persist, or later writes replace them. Only a capture that
observes the failing write can support a producer-specific change. The physical
baseline and candidate integration remain outside this diagnostic.
