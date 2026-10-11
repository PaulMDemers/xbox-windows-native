# Actual DMA/backend byte capture

This diagnostic changes only the emulator observation path. Reconstruct the
685f24e3 candidate from its complete pinned source manifest before adding two
C-file hooks and a private header. Build in a private copy on E: with the existing
pinned toolchain image. Never edit the shared emulator source or guest drivers.

Each component emits little-endian 128-byte headers followed by bounded raw
bytes. Fields: magic, version, sequence, request ID, phase, disk offset, byte
count, QEMUIOVector address, owner address, signed return status, monotonic host
microseconds, vector offset, captured payload length, flags, vector count,
reserved. Phases: DMA begin 0, actual mapped submission 1, callback before unmap
2, final DMA completion 3, backend submission 4, backend return 5, SG descriptor
11. Descriptor offsets are guest physical addresses, not disk addresses.

Capture writes at or above the known F partition offset 8004132864. Maximum
payload per event is 1 MiB; a component file caps at 256 MiB. Flag bits 63 and 62
record an uncaptured range or cap respectively. Reject incomplete/truncated
records and do not qualify partial captures. Flush each host evidence record;
that flush applies to the evidence log, not guest storage. Logging failures abort
the diagnostic rather than silently discarding evidence.

DMA request IDs are monotonically assigned before the first callback and kept
in DMAAIOCB through chunk completion. Capture actual mapped QEMUIOVector bytes
immediately before io_func, and again at dma_blk_cb before offset advancement or
unmapping. Preserve SG physical addresses/lengths and final DMA status. Backend
IDs live in the suspended coroutine across bdrv_co_pwritev_part; capture before
that call and immediately after its asynchronous completion returns.

Associate a backend pair with one DMA chunk only when vector address, virtual
disk byte range and complete timestamp nesting agree uniquely. Preserve errors,
unmatched calls, reused pointers, missing completions and changed buffers.
Compare the final successful submission snapshots with independent cold reads of
all allocated payload/status/exit and registry-hive clusters. Flag overlapping
in-flight ranges instead of silently assuming an order.

The observer launches Windows once, makes no debugger attachment or guest input,
and retains its 300-second watchdog. No setup-dialog actions or normal-shutdown
claims are added. Instrumentation still changes host timing, and backend success
is not a power-loss durability guarantee. A failing cold byte must be traced
before attributing corruption to FATX, ATA, DMA or the emulator backend.
