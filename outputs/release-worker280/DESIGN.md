# Three-boundary release worker proposal

280 implements and host-tests the proposed worker orchestration that was missing
from279. It is not a compiled renderer integration. Runtime graph/UI authorization,
the real wrapper around279, post-release snapshots, and the QOM request/getter
adapter still need implementation. Their interfaces are explicit host models in
test-worker.c. No guest, shared source, native driver or physical console changed.

## States and acknowledgment epochs

All three X265State slots and their bounded ledger buffers must be allocated
before the initial request is published. The slots never reset or alias. State1
accepts the initial worker once; state2 owns execution; state3 permits guest
resume only after both the pre-release and post-release boundaries succeed.
The future stopped-guest end request changes3 to4 once. The same worker consumes4
and publishes5 after the end boundary and seal, or6 on any refusal/quarantine.
State5 means the transaction finished, not that independent guest qualification
passed. Complete273 accounting and independent pixel/native checks remain required.

Pre-release uses actual CPU epochs1/2, post-release3/4, post-resume5/6. Each capture
retains the original FIFO/pending/report/primitive checks, actual owner and native
contexts, finite render/display fences, CPU-exclusive acknowledged inventories,
and renderer/PG locking. Locks are dropped before CPU jobs and fences as in278.
Capture succeeds with renderer/PG locks held; the caller must release them. On
failure capture releases them itself. The host harness checks these paths.

Within each capture both callback inventories and locked surface graphs must be
complete and equal, with a stable nonzero mutation clock. Across the first two
captures the clock, CPU owner, callback tuples, surface tuples, selected identities,
names and source/palette ranges must remain equal. Across actual guest resume the
clock may change, but each new pair must be internally stable. Selected identities,
keys represented by ranges, names, refcounts and owner/context identity still match.
The full TextureKey/hash/content proof remains the real observer/controller's job.

The original277 contract and279 helper are byte-identical copies. New280 common
validation derives from277 with only explicit three-stage/refcount rules. Control
retains refs2/cache1/unit1 in all stages. Candidate requires actual refs1/cache1/
unit0 only at stage2, and refs2/cache1/unit1 again at3. No observed field is rewritten
to satisfy277 and no fake zero callback count reaches274.

## Mutation and quarantine

The proposed worker first captures the complete pre-boundary, asks the future
actual unbound-graph provider for279 evidence, then arms the real generation
observer. Only successful arm sets observer_armed. Deadline/quiescence are checked
again after the potentially slow initial snapshots and before the release call.
The candidate invokes279 exactly once. Control never invokes it. A partial or
unexpected result preserves the actual mutated_mask and quarantines the run.

Fresh post-release capture and exact retained graph comparison occur while the
guest is still stopped. The graph comparison changes only a local expected copy:
the four unit pointers/dirty bits and their reference accounting. Actual evidence
is immutable. Any unrelated row difference refuses. The proposed post-snapshot
interface must perform independent source/GL readback at stage2 without generating
a fake bind or changing the first real guest-bind snapshot state.

Only after all of that may state3 restore the prior FIFO halt. Any failure after
mutation keeps it halted; there is no rollback, refcount assignment, host binder,
callback removal, dirty-surface download, join, finalizer, reset or renderer switch.
Metadata and outstanding CPU job storage must remain alive through process teardown.

## Transport and verification

Every capture publishes the original bounded scalar rows once, plus71 for actual
worker/timing/deadline and72 for each CPU epoch/thread/acknowledgment time. A failed
append is not retried. Transaction records are fixed16-word scalar copies, one
initial and one end record. The getter must acquire the overall terminal state
before reading; a completed individual slot is not permission to resume the guest.
The proposed binary host transport has an independent little-endian decoder;
the runtime getter/serializer still needs implementation and its own frozen tests.

Host004 compiles the exact proposed capture/orchestration/validation/comparison/
publication bodies with ASan/UBSan. CPU jobs, GL/context work, full graph collection,
runtime unbound authorization, release call and snapshots are explicit models.
Graph001 separately compiles the exact live-cache collector with real QEMU queue
macros and modeled objects. Publication001 tests the actual record writer under
real pthread release/acquire races, but the caller/getter is modeled. Transport001
decodes actual host-output bytes and rejects changed/incomplete metadata. None of
these results establishes actual GL, a guest release, performance or GPU ownership.

The graph collector resolves a saved scalar identity through a current live cache
edge before dereferencing. A missing cache owner refuses. Generation tombstones and
actual bind/free accounting remain necessary; scalar pointer equality alone does
not exclude ABA. Full known-context ownership must be derived at runtime, including
the immutable UI capture. Unknown extension/object ownership still refuses.

Strict278 disk equality remains false.279's BRFR/PowerCycleCount interpretation is
an inference, not writer attribution or a gate waiver. Dirty surfaces with unknown
native provenance remain untouched outside this narrow operation. Native Windows
PTE/cache aliases and deferred release remain separate before any native GPU copy.
