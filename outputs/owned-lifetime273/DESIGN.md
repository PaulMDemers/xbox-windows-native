#273 lifetime accounting and terminal boundaries

This is observation only. The unchanged normal binder and destructor call the
observer on the PFIFO owner. It never invokes the binder, releases a reference,
changes guest commands, creates/deletes GL objects or writes guest memory.
Each initial identity has an immutable generation. Final-free observation occurs
before the original decrement/free and immediately tombstones that identity;
later address reuse cannot revive it.

The BYTE-IDENTICAL270 core reserves four first-bind and four final-free records.
Other events use128 exact run records with64-bit saturating sequence/counters.
A run includes identity, generation, kind, slot, code, first/last sequence and
count. Only contiguous identical events coalesce. Saturation remains sticky;
reserved records remain useful for diagnosis but cannot repair missing coverage.

The existing one-word gate has active and closed bits. Admission requires the
actual owner thread. Sealing disables admission and atomically closes the gate;
an active callback prevents publication until it releases the active bit.
Terminal publication is one-shot, with exclusive file creation. A failed write
or close permanently fails publication. First-bind snapshot failure is also
sticky and cannot be retried to substitute a later successful image.

terminal273.bin has an explicit little-endian format:16 header words, four20-word
watch records and up to128 eight-word runs (768..8960 bytes). The header carries
gate/core/transport errors, actual owner, closed/disabled/sealed state and the
four capture bits. The independent decoder checks exact length, finite counts,
identity/generation, reserved lifecycle ordering, contiguous sequence intervals
and counter totals without expanding a hostile count. Every error source must
be zero. Actual acknowledged seal and the final live error report must also
match; successful file writing by itself is not successful qualification.

The observer retains the inherited GL snapshot code: bounded source/palette
copies, canonical RGBA readback and restoration of pack state, PBO, active unit
and binding. Double sampling establishes only observed source stability, not a
general CPU ABA exclusion. Snapshots stay private. New standalone validation
must compare them against the independent owned271 texture oracle and actual
translated payload ranges, plus guest framebuffer evidence from272's protocol.

## Remaining owner boundary

Exact269 renderer.c x260_cpu_boundary queues an acknowledged CPU-exclusive job;
an empty work list alone is not completion. x260_context_fence uses finite
render/display fences outside FIFO/renderer/PGRAPH/BQL locks. Initial265 capture
uses both helpers around its immutable graph. Conversely, the existing
pgraph_gl_ledger265_request seal269 branch merely checks stopped CPU/completed
initial capture and calls the observer seal. PFIFO can still be independent of
that monitor action. Guest pb_busy is not a host completion acknowledgment.

A NEW terminal actor must have separate never-reset state, lifetime and epoch.
Publish it under FIFO synchronization only after actual stopped checkpoint and
closed frontend checks. The PFIFO worker must acknowledge entry, verify actual
GET/PUT and method/error state, run both CPU-exclusive inventories and finite
render/display fences, inspect pending predicates and seal on the original
owner. Keep actual native context identities and GL selection restoration in
the record. Unknown edges, active work, wrong owner, deadline expiry or changed
inventory refuse; do not clear pending bits or force completion. No joins,
whole finalizer, renderer switch, global reset or native grant are permitted.

Review actual lock order before implementing. CPU jobs remain allocated after
timeout; their metadata cannot be freed while queued. Release FIFO during waits
and GL fences, never acquire BQL while holding graphics locks, use bounded
trylocks for graph inspection, and retain the outer owned-process watchdog for
calls without cancellation. A failed transaction quarantines the attempt; no
fabricated rollback. A successfully sealed accounting log is only one part of
the next control, not a proof of complete GPU retirement.
