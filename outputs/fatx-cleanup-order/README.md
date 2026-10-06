# Cleanup lock-order causal candidate0099

The unchanged0098 concurrency diagnostic reproduced an exclusive ownership
cycle: cleanup held the volume namespace lock while waiting for worker0.bin's
MainResource; volume flush held that MainResource while waiting for the same
namespace lock. The matching kernel PDB and compiled0098 field offsets identify
the resource addresses. The original64MiB snapshot remains private and retained.
See [the evidence](../fatx-shutdown-concurrency/001/deadlock-summary.json).

0099 moves ordinary-file cleanup's MainResource acquisition before DirResource.
The open FILE_OBJECT retains its FCB during cleanup; release occurs after the
namespace lock, before IRP completion. Volume cleanup keeps its existing path
because it does not acquire a per-file lock and may delete its VCB. Paging/cache
teardown, handle/share counts, delete semantics and metadata persistence remain
inside the existing cleanup body. No physical binary is changed.

This is deliberately a causal candidate, not a general lock-order qualification:
overwrite-create, enumeration and selected metadata paths still contain the
reverse order. The same concurrent test must run against this change, with any
new cycle retained and fixed separately. Do not deploy it based on compilation
or claim all previous physical failures share the captured cause.

The source generator validates0098's tree and applies the new patch only in a
temporary Git index to derive a new manifest. The build reconstructs that entire
manifest into an independent source directory under the existing build lease.
An initial build preflight stopped before creating its output directory because
C: had less than the20GiB reserve; it is not a compiled or runtime attempt.
