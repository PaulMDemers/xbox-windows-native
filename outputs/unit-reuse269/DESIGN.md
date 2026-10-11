#269: observe real guest texture reuse before releasing any unit reference

Exact267 renderer child, unchanged265 native checkpoint probe and258 reboot-held
CPU arena driver. No268 release helper is installed. No refcount, cache eviction,
shader join, guest data, guest command, device policy or GPU ownership change.

At the existing immutable ledger capture, the PFIFO owner arms four original unit
identities only after complete graph/context collection, zero unknown shader work,
balanced counted references and zero CPU callbacks. Each must be disabled,
refcount2, distinct and have one actual cache owner. Both CPU boundary audits and
normal frontend teardown remain. Initial raw snapshots happen with the guest
stopped and UI closed. Existing UI BQL lock behavior is unchanged, not extended.

The observer inserts hooks after the two normal bind paths and immediately before
the original counted decrement. A final decrement permanently invalidates the
watched generation before the actual free. No later address or GLuint reuse can
revive it. First real bind of each still-live identity captures one more snapshot.
There is no direct host call to the binder. A different PFIFO thread, concurrent
entry, snapshot failure or saturated event stream sets a terminal atomic error.
The existing report exposes that error. After dashboard return the host stops the
CPU and requests a one-way observation seal, which disables new hook entries and
requires any current entry to finish. Active and permanently closed bits share
one atomic word; entry is CAS0-to-active, sealing atomically sets closed and exit
clears only active. Only after seal acknowledgment does
the host read the terminal error and close xemu orderly. No actor is reset and no
renderer object is disposed. A normal return alone is never reuse coverage.

Snapshots use bounded2MiB source and2MiB canonical RGBA8 limits per object, at most
4096 palette bytes, four initial/four later snapshots and128 events plus one
overflow marker. Only positive-sized2D normalized-red textures are accepted.
Actual width/height/internal format, identity, generation, data hash/draw time,
cache key bytes, raw source/palette and canonical GL bytes are preserved privately.
No proprietary image data is committed. Readback restores and verifies active
unit, unit0 texture binding, pixel-pack buffer and all eight GL4.0 pack parameters.
Actual context identity must match the render context. GL/file calls have the
outer run watchdog, not independently cancellable per-call deadlines.

Before/after source copies detect an observed change during capture. Matching
copies do not prove absence of arbitrary ABA writes or CPU-exclusive ownership
after resume. Equality is an observation of sampled bytes and GL content, not a
general concurrency proof or final-frame correctness. This limitation must be
resolved before any broader release/ownership claim requiring that guarantee.

The independent host parser rejects altered generations/identities/context/thread,
bad lengths, missing/truncated events, snapshot/bind mismatches, overflow/errors
and binds after final deletion. It compares cache key, source, palette and pixels
byte-for-byte as well as semantic metadata. All four must actually bind and remain
unchanged to cover a four-unit release. Changed data is not ignored; partial/no
reuse is a failed coverage result, preserved without rerunning until lucky.

Normal guest restart is the initial specific discriminator. If these old textures
do not survive/rebind unchanged, use a genuinely owned guest graphics workload
instead. No borrowed firmware commands, forced reset or whole finalizer shortcut.
Full cold workload/allocation/hive/protected-file audit and normal shutdown/orderly
host exit remain required; inherited Ftdisk49 remains a strict event failure.

Compiled002 lacked terminal sealing and was never launched. Compiled003 added a
two-variable seal, but the exact-function host race test failed: separate enabled
and busy loads allowed stale observations. Failed host001 and both compiled
predecessors are preserved. The corrected one-word gate requires a new build and
new host result; no guest ever used the failed handshake.

Build004 compiled the corrected gate but preflight rejected a new printf format
warning for the thread ID. Build005 changes only that explicit uint64 cast; the
exact tested entry/seal functions remain unchanged. Neither002,003 nor004 launched.
