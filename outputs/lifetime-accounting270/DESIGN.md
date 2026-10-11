#270: preserve lifecycle evidence without an unbounded event stream

This is a host-tested accounting component, not an installed renderer observer.
No renderer, native driver, SDK or physical-console state is changed. The existing
269 observer and its failed runtime remain immutable.

Four original registrations have distinct opaque identities and generations.
They cannot be reset or reused. The acknowledged single renderer owner must call
the component under the existing one-word active/closed gate. The accounting
component never reads a renderer pointer or derives a generation from an address.
The future adapter must match live identity before reading refcount, invalidate
the original generation before final free, and never follow a dead pointer.
Unexpected reuse of a tombstoned address must refuse qualification rather than
revive an original generation. Ordinary unrelated objects are outside the watch;
their hooks must not be passed off as a watched lifetime.

Each watch reserves one first-bind record and one final-free record. All callback
observations share a monotonic 64-bit sequence. Repeated binds and nonfinal
decrements occupy at most128 run records. A run merges only consecutive sequences
with identical kind, slot, generation, identity and code. Per-watch bind/decrement
totals are exact saturating 64-bit counters. First binds and final frees split
runs; the complete sequence is independently reconstructable from the two stores.
The final-free code records the actual pre-decrement refcount1. These records
describe observed callbacks, not inferred refcount deltas or GPU completion.

Run/counter/sequence overflow and malformed or stale identity/generation input
produce sticky errors. Reserved lifecycle slots remain available after run
overflow for diagnosis, but cannot turn the result into PASS. Sequence exhaustion
records a zero, explicitly invalid sequence with a sticky error. There is no
wrapping arithmetic, approximate counting, dropped-event waiver or retry/reset.

The core's l270_complete means accounting has no reported error, ONLY. A future
complete-observation qualifier must also require acknowledged seal, zero gate and
transport errors, exact source/binary pins, source/GL snapshots, four actual guest
binds, requested lifecycle coverage and independent pixel equality. An empty
successfully armed core is not guest coverage. Terminal serialization must occur
only after the one-way gate acknowledges no active writer. The host test uses
the exact269 entry/seal functions with C11 atomic equivalents and checks the
published core stays byte-identical after acknowledgment and subsequent join.
The test join belongs to the host harness, not to renderer retirement.

All129 original269 event files are hash-checked against the existing final report.
Only the127 fully captured bind/decrement callbacks before its overflow marker
are replayed. They reconstruct exactly using seven runs plus one first-bind slot.
An explicit external-incomplete error then rejects that historical input. This
compression result cannot reconstruct the missing tail or rehabilitate269.

Host tests also cover one million identical decrements, mixed binds/decrements,
all four final frees, run overflow followed by reserved lifecycle capture,
counter/sequence exhaustion, stale and reused addresses/generations, duplicate
registration, invalid slot/refcount/path, busy/foreign-owner refusal and4096
entry/seal publication races. ASan/UBSan cover the actual proposed accounting code;
no actual GL callback, shader, renderer thread or guest is executed in these tests.
