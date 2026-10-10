#226 serialized ownership transition prerequisite

This implements a portable ordering/range reducer for a future resident NT5
adapter. It performs no MMIO, allocation, interrupt acknowledgment, reset or
GPU submission. It is not a security boundary or a source of actual ownership
evidence: a caller can fabricate receipts. No runtime adapter exists in226, and
the actual225 state remains refused. Synthetic host success must never become
a native grant. The reducer compiles with the pinned project RosBE i686 compiler.

## Exact inputs and limits

`inventory001.json` pins12 files from the actual compiled xemu candidate manifest:
five unchanged renderer sources plus seven privately reconstructed candidate
sources from215. The examined files retain the existing resource-model and CPU
surface-eviction changes. No borrowed source was modified.225's independently
reviewed closed trace remains the actual loader evidence; no old run was replayed.

The whole inherited RAMIN10000..15000 aperture is protected, including bytes
that happen to look empty and each observed descriptor's uncaptured extension.
The4KiB RAMHT is fully captured with22 valid entries, but that is not an allocator
census. RAMFC00890110 yields normalized fields68/68/1 under the pinned masks;
these are fields, not byte addresses or verified extent sizes. RAMRO0 also is
not evidence that no runout storage can be referenced. Neither has consumers
beyond definitions in the12 examined model files. The actual physical backing,
channel contexts and other old-engine references remain unresolved.

The envytools [NV1:NV4 PFIFO documentation](https://envytools.readthedocs.io/en/latest/hw/fifo/nv1-pfifo.html)
describes older RAMFC/RAMRO structures. It was consulted as a lead only; its
variant-specific sizes cannot qualify an NV2A range. Local pinned pbkit reference
likewise shows two64-byte channel records and an adjacent unknown32-byte area,
but its allocation convention does not establish all inherited owners. No
NV1-size substitution or spare-memory claim is made.

## What the actual model does

PFIFO broadcasts `fifo_idle_cond` when its worker has no kick and is going to
wait. A puller blocked on context switching or inaccessible PGRAPH can still
retain an unconsumed method. Therefore that signal is a worker scheduling fact,
not queue consumption or renderer retirement. GET==PUT also leaves the parsed
method-count and backend/reference obligations separate.

OpenGL's shutdown trigger/wait only requests and waits for shader-cache
writeback. Vulkan's corresponding hooks are empty. The OpenGL surface flush
invalidates cached surfaces with the download-all-dirty call commented out;
its flush-complete event is not a preserving ownership transition. Vulkan flush
does call `pgraph_vk_finish`, but neither renderer event alone proves stopped
producers, empty command state, CPU-visible results and ended references. These
are matched-source findings, not a new emulator execution or hardware diagnosis.

Software context switching traps the desired channel and stops the puller.
Acknowledging its IRQ clears the wait. An adapter must install and read back a
private valid context for exactly its requested/trapped channel BEFORE that
acknowledgment. The existing miniport has no qualifying handler. No inherited
handles, descriptor snippets or guessed context-image layout may be reused.

## Implemented transition contract

Callers serialize one owner context, retain its immutable copied plan and use a
monotonic clock. Preparation requires complete inherited ranges, verified
backing, supported backend retirement and context service; unknown facts refuse
without exposing resources. New instance ranges must be aligned, bounded within
the1MiB model aperture, mutually disjoint and disjoint from every old range. This
model bound is not proof a physical allocation exists. Test20000/22000 ranges
are synthetic only.

Each operation is opened with `x226_begin`. Exposure is recorded BEFORE even
the first producer/configuration write. The adapter then performs the bounded
operation and returns a receipt paired by generation, action and sequence. A
stale unrelated receipt cannot satisfy or cancel a current operation. Current
failure/incomplete evidence quarantines. The initial sequence is:

1. Revoke producer admission and receive actual confirmation.
2. Retire old work: require producer stop, consumed queue, finished backend and
   ended references independently.
3. Install exact private descriptors/table/context backing from the owned plan.
4. Service only the own-channel context request; verify context before IRQ ack.
5. Submit a bounded command once. No other operation may bypass these stages.

An exact nonzero generation token changes SUBMITTED to COMPLETED only. It does
not release the allocation. Release additionally requires new-producer stop,
queue/backend/reference retirement, then an explicit safe owner restoration
with ended references. Completion, backend retirement and restoration remain
different operations. A restore receipt cannot arrive directly from COMPLETED.

The same absolute budget covers the whole transition. Clock regression,
deadline expiration, current operation failure, unexpected token or cancellation
after exposure is terminal quarantine. Late receipts/tokens cannot revive it.
Only cancellation before exposure can release directly. The adapter must tick
while waiting; invalid requests do not replace the timeout watchdog. No global
reset, recovery release or arbitrary retry is provided. Quarantine must retain
resident allocations and locks across crash/display ownership handoff.

## Required adapter stores and provenance before integration

| Operation | Matched consumer | Required evidence before its first store |
| --- | --- | --- |
| Producer revoke | PFIFO PUSH0/DMA_PUSH/PULL0 and PGRAPH FIFO in `pfifo.c` | All producers serialized, prior register owner and actual stop behavior; preserve an in-flight consumer rather than disabling it prematurely |
| Old retirement | PFIFO worker and renderer pending paths | Consumed parser/queue state plus preserving backend fence/download and ended CPU/GPU references; no use of shutdown/flush as a shortcut |
| Instance install | RAMHT lookup in `pfifo.c`, DMA map in `nv2a.c` | Complete allocator ranges, old references retired, actual aperture/UMA translation and CPU cache visibility, exact separate private table/objects |
| Context service | `pgraph_context_switch` / `pgraph_write` | Resident handler, request/channel pairing, genuine private context initialization/readback, bounded IRQ acknowledgment after verification |
| Submission/completion | USER and class62/9f/97 protocol from215 | Pinned adapter and exact owned DMA pages, store ordering, new token cleared and visible, finite submission and completion |
| New retirement/restore | Actual adapter and preserving renderer/backend | Producers stopped, all references ended and safe prior-owner restoration; a token cannot authorize free |

These are obligations, not an approved write list. There is currently no
candidate store or native permit. PTE/cache alias coherence and native deferred
cleanup fallback faults from earlier checkpoints remain separately unqualified.
The physical0101/video0093 baseline,0088 rollback,0.1.0 and all failed evidence
are unchanged. No physical access or other-device integration occurs here.
