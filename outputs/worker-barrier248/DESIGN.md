#247 worker checkpoint

This emulator-only diagnostic extends the pinned246 UI gate. Native drivers,
settings and actual224/219/211 device policy remain unchanged. One fresh fixture,
one request and one explicit release; no old attempt is replayed.

The host stops the CPU at the pinned FreeLoader entry, acknowledges the UI close,
then requests FIFO producer admission halt using a trylock. The PFIFO worker
claims the request before pending work, pusher and reports. Renderer/PG locks are
try-only for its immutable surface inventory. Nonempty commands, pending work,
draw state, wait/switch state, surface flags or another loan explicitly refuse.
No completion register, wait flag, dirty flag or native permit is manufactured.

After dropping all FIFO/PG/renderer locks, the actual worker selects each existing
render/display context, records seven current GL bindings and waits at most100ms
on a newly created diagnostic fence. Only that fence is deleted. The worker
restores render context, publishes the immutable record and parks on a20ms timed
condition wait that releases FIFO. The whole request has a five-second deadline.
Explicit release or expiry restores the original halt value; the host waits for
that terminal acknowledgment before reopening the UI and resuming the CPU.

This closes worker admission for the observed checkpoint; it does not retire
shared objects, join shader save threads or remove CPU callbacks. Context pointer
values identify selected existing contexts, not an independent platform query.
GL current binding identities do not enumerate every retained cache reference.

The existing natural flush additionally records each surface pointer, range,
buffer and latest dirty/download/CPU-eviction/upload flags immediately before
its ordinary invalidation. This is observation only.247 does not preserve dirty
GPU bytes at that later disposal or change its existing commented-out download.
A flagged checkpoint refuses instead of declaring clean ownership. Earlier227
readback is not evidence of latest contents after an unobserved subsequent draw.

Qualification requires paired actor events, two successful fences, a measured
parked interval without pending/surface/frontend work, successful worker/UI
reopening, normal guest restart and complete offline allocation/hive/protected
audits. Strict events remain independent; inherited Ftdisk49 is never waived.
Host adapter tests verify the actual compiled helper's lock and failure paths;
actual GL completion must come from the new runtime, not those adapters.
