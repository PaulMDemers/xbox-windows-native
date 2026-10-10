# Next bounded consumption experiment

231 observed GET03fc49b0 / PUT03fd4c70: a66240-byte numerical gap with
DMA_STATE00000104, method count0, error0, push/pull/DMA/PGRAPH access1,
DMA_PUSH suspended status0. Request and worker-gate snapshots match exactly.
The parser did not report an error or a remaining parameter count at this gate.
This does not prove the command stream is valid or immediately consumable.
No actual consumption was attempted in231.

Use a NEW opt-in model/unique fixture. Keep the vCPU producer stopped for the
whole diagnostic. Capture waiting_for_nop/flip/context-switch and the relevant
push/pull conditions, then run the actual existing parser/puller with explicit
iteration/processed-word and real-time budgets. Bound jump/call-only cycles as
well as method packets; retain the exact stopping cause and raw before/after
GET/PUT/parser state. A numerical gap alone is not a full stream census.

The actual pusher can release FIFO lock while invoking PGRAPH methods. Account
for that lock transition, lookahead and every early return; do not independently
write GET, parser counts/errors, FIFO-access bits or status to manufacture idle.
Respect existing flip/context/nop waits. A wait requiring the stopped guest's
interrupt service must be reported as a stall, not bypassed. Do not briefly
resume the vCPU to obtain a clean result.

One-shot terminal publication must retain231 release/acquire ordering and
timeout tuple withholding. A timeout or unsafe error keeps quarantine through
the owned process's bounded exit. GL calls cannot all be cancelled by a loop
budget: retain an independent owned host watchdog and no Windows launch after
uncertain failure. A normal refusal can restore prior halt under FIFO lock.

After actual consumption, require genuine empty parser/queue predicates before
the existing surface-preservation checks. Dirty GPU-to-CPU readback needs real
positive coverage and exact reserved-memory comparison. Existing frontend and
backend references remain retained by the current diagnostic even after a
preserved result; no native permit follows from a drain or report state alone.
Full inherited allocator/backing census, private context service and CPU alias
coherence are still independent prerequisites for the native16x8 test.
