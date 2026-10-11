# Next: actual guest acknowledgement and producer handoff

Never repeat closed234 trace002 or failed preparation001. Snapshot publication
works in its narrow scope; it did not close a firmware producer, retire frontend
references or make the stopped NOP wait consumable. Immutable live current data
must never be called a later stopped sample. Preserve all overwritten/missing
boundaries and exact ERROR mask/guest INTR distinction.

Next NEW bounded diagnostic should identify the actual executing guest handler
that acknowledges NV_PGRAPH_INTR_ERROR and the loader's last firmware producer/
instance/channel transition. Freeze the owned loader/kernel identities and pin
resident executing bytes; static code leads alone are insufficient. Derive a
specific observable guest close/quiesce event before planning a new request.
No state-clearing, host resume inside the accepted stopped request, global GPU
reset, borrowed firmware channel or repeated empty-queue search to force success.
Snapshot journal, queue consumption, surface preservation, reference retirement
and native ownership are separate gates. No native acceleration/HD mode claim.

Any new approach must keep FIFO->PG ordering (never take FIFO under PG), avoid
BQL blocking, have finite capture/request/watchdog and complete owned teardown.
Keep actual CPU workload/normal shutdown/cold allocation/hives/protected hashes/
policy/events; warnings/errors retain strict failure. One boot does not settle
USB's separate repeated-boot stale marker/two invalid hives (ccd210f). Physical
baseline0101/video0093,0088rollback,immutable0.1.0 and failed evidence stay intact.
No physical deployment or device merges in this phase. Respect20GiB build guard
and cooperative build/xemu leases; preserve exact runtime/frozen identities.
