# Next fresh diagnostic: observe the actual NOP wait lifecycle

232 refused before dispatch because waiting_for_nop was already set. Zero
iterations/committed words and identical GET/PUT do not exercise the guest
parser/puller. Never rerun this closed case or clear the wait to obtain a pass.

The byte-pinned compiled pgraph.c has two assignments: nonzero NV097
NO_OPERATION records the trapped method/data, sets ERROR interrupt and the
wait, then updates IRQ; the ordinary guest NV_PGRAPH_INTR acknowledgement
clears supplied pending bits and clears the wait only once ERROR is absent.
These are static producer/clearer leads. 232 did not record the trapped method,
parameter, pending/enabled interrupt masks or actual guest acknowledgement.
The wait name is not proof of which request created the observed instance.

Build a NEW owned emulator child with a bounded, read-only diagnostic record
of those actual producer and acknowledgement sites. Pin the actual compiled
PGRAPH/NV2A source and executable. Record sequence, pending/enabled interrupts,
NSOURCE, trapped address/data, raw wait bits and queue/parser words before/after
the existing operations, under their existing locks. Use bounded resident
storage, not an unbounded log or lock-order change. Distinguish a guest IRQ
acknowledgement from backend maintenance, reset and arbitrary sampling.

Observe the ordinary guest's interrupt handling before a separate stopped-CPU
handoff. Do not resume the producer inside an accepted preservation request,
retry the request or synthesize a successful completion. If the owned handoff
boundary is still waiting on the guest, preserve the refusal. Any later
protocol needs an actual guest-side producer-close/quiesce acknowledgement
before freezing; a momentary empty queue is not ownership.

Require complete observer/guest cleanup and fresh cold allocation, hives,
protected hashes, event deltas and unchanged device policy. Preserve strict
Ftdisk49 failure. No physical deployment, device integration, native GPU grant
or release tag change. All frontend/backend references, dirty readback,
allocator/context/alias prerequisites remain independent unqualified gates.

USB's independent no-XID second-boot stale-data/orphan failure (reported at
4a2f1f6) is unresolved. Root's one first-boot/restart selected cold checks do not
qualify repeated-boot storage; keep those results separate.
