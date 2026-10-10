#227 opt-in emulator backend preservation

This is an actual xemu OpenGL worker implementation, not a guest or native
ownership adapter. It changes five sources relative to the exact compiled
prior candidate. The stopped-VM QOM property `xwn-preserve227` accepts one
request per instance. Its report always says `references_retired=0 native_grant=0`.
No guest MMIO register is added, firmware handle reused or physical driver changed.

The monitor setter refuses running VMs and unsupported renderers; it try-locks
PFIFO rather than waiting on a worker which can need the BQL. Once accepted it
records the old halt, a five-second monotonic deadline and halts worker admission
before queuing the request. The actual worker validates GET/PUT and parsed method
count/error independently. That is a model queue predicate, not physical idle.

The GL worker try-locks the frontend renderer lock, then uses its existing
PGRAPH lock. Active primitives/batches, framebuffer users, wait conditions and
pending flush/sync refuse before readback. The complete surface list is checked
before GL work: at most128 surfaces, each bounded16MiB with actual in-VRAM extent,
and all cached ranges disjoint. Overlap is refused rather than selecting a
winner. Nonlinear pitch/size conventions outside the predicate remain unsupported.

An actual GL fence waits only the remaining request budget. For each dirty or
pending-download surface the worker initializes a private expected buffer from
VRAM (retaining padding), reads GPU pixels through the existing conversion path,
then invokes the actual surface-download path and compares the full buffer span
byte-for-byte. A final bounded fence follows all downloads. No cached surface,
callback, texture or context is destroyed. The ordinary old flush path is not
changed or used. Reported bytes are exact compared buffer spans, not a claim
that every padding byte was written by the GPU.

The independent readback uses the same conversion implementation: it checks
preserving transfer into VRAM, not independent rasterizer/format correctness.
Actual nonzero dirty-surface coverage is required separately. Zero dirty surfaces
cannot qualify byte preservation, even if the two fences complete.

Successful preservation or a pre-work refusal restores the exact prior host
halt. Failed/expired operations retain it. The report getter can atomically mark
an in-progress request timed out; late worker results never restore admission.
Host wait is bounded, but GL readback calls themselves are not cancellable. A
stuck host driver requires the owned process watchdog/cleanup; no claim of a
hard execution bound inside external graphics APIs is made. No memory is freed
on a late result. There is no reset/retry operation in the property.

The harness pauses at the actual code-pinned Cromwell producer-exit entry from
closed225, while retaining its exact binary. It does not modify guest registers
or memory. It owns the monitor lock until the one accepted request is terminal,
retains before/after RAMIN and reserved-tail bytes, tears down its breakpoint
and resumes only a completed or refused operation. Any uncertain accepted
request remains paused and is closed by the owned watchdog rather than resumed.
The new emulator/property path is diagnostic intervention, not ordinary native
qualification. Normal CPU workload, event gates, full cold allocation, hives,
protected payloads and device policy are checked independently after closure.

Build001 failed before its first borrowed-source write (WSL ownership);
build002 failed before preparation (scoped git ownership). Both inputs are
retained. Successful003 lacked the later exact readback comparison; successful004
lacked the later alias refusal. Both are prepared, NEVER launched, and hash-
verified offloaded to E through original-path junctions. Only005 is the candidate
for the single new trace001. Each build restores borrowed sources. Resource
refusal before005 acquisition did not start a build or guest and is distinct
from a build failure. No frozen old experiment is rerun or modified.

Physical0101/video0093,0088 rollback, immutable0.1.0 and all failures are preserved.
No physical FTP/deployment/testing, device policy changes, event suppression or
ownership grant. Full old RAMFC/RAMRO allocation/backing, actual native context
service, reference retirement and PTE/cache alias coherence remain unresolved.
