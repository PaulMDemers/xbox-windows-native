# Bounded read-only pending-work preflight224

This adds sixteen approved FIFO/graph register observations to the actual222
FileObject/token/bounded-mutex bridge. Matched OFF/ON drivers use shared context
and sampler objects and identical probe code. OFF performs no maps/reads; ON
maps only fd002000..fd003fff and fd400000..fd400fff uncached. A valid CPU owner
generation permits eight immediate sequential rounds,128 reads total. Wrong
owner/stale generation/short input are rejected before reads. Host substitutions
also exercise reserved fields, IRQL, lock failure and partial-map cleanup.

There are no new register stores, RAMIN/USER mappings, descriptors, channel
borrowing, resets or GPU grants. Successful mapping persists until normal reboot;
there is no unload callback. EXPOSE retains222 HOLD and its cleanup discipline.
CPU allocation does not convey GPU instance/channel ownership.

The pinned xemu model does not maintain DMA-pusher busy. RUNOUT_STATUS reads as
empty, and PGRAPH_STATUS has no hardware implementation. GET==PUT can stop the
pusher before a residual method count is consumed. Disabled push/pull is not
retirement. Backend reports/surface queues have independent lifetimes. Therefore
every reply retains NO_OWNERSHIP and UNMODELED_BUSY, including otherwise quiet
snapshots. OBSERVED means bounded observation completed, never drained/idle.
These sequential words are non-atomic and cannot prove stability between calls.

The ordinary pair must retain222 CPU65 allocations/releases/refusals,3194880
verified bytes/four joined workers plus explicit224 raw observations, normal
shutdown/dashboard, full cold allocation, five structural hives, protected
hashes, typed device policy and unchanged event gates. Exact211 targeted Cancel
helper and physical-core parent policy remain inherited_null_policy FALSE.
Source-derived read counts are separate from debugger instrumentation. A scope
PASS never waives inherited Ftdisk49 or establishes whole-boot qualification.
No physical access or device branch integration is part of this checkpoint.

Preserve failed build001 strict-aliasing harness warning, its exact inputs and
failed native import-review assertion. The host buffer copy and provider-review
corrections change no native source/binary. Before additional GPU work, establish
genuine producer retirement/instance ownership and bounded backend drain from
runtime evidence. This preflight deliberately cannot supply that capability.
