#274 terminal ownership transaction

This opt-in observation extends exact273, which extends exact269. It does not
install268's proposed release helper or grant native GPU ownership.

The existing initial capture remains a one-shot265 actor. X265State gains a
separate end274 pointer, published only once after stopped CPU, closed frontend,
completed initial capture, current OpenGL renderer and armed/error-free observer
checks. Allocate the second graph before taking FIFO's trylock. Once published,
the end state and asynchronous CPU-job metadata remain alive until process exit,
including on timeout. There is no actor reset or retry after acceptance.

The unchanged PFIFO callsite services the selected actor. Initial and terminal
captures use separate stages1/2, hence CPU acknowledgment epochs1/2 and3/4.
The worker checks the original owner, current context, framebuffer loan, guest
stop and finite10-second transaction deadline. It queues an actual exclusive
CPU job, releases FIFO for finite render/display GL fences, restores render
context and takes renderer/PGRAPH trylocks in that order. Terminal admission
also requires equal DMA GET/PUT, zero method/error bits, no pending predicates,
active primitive, queued reports or queries. No pending field is cleared.

A new full ownership graph uses the original bounded collectors. It retains
cache/unit/binding counts, known container/indexed references and shader work
function acknowledgments. Native render/display context rows must match the
initial identities exactly. Unknown reference accounting or unfinished shader
work refuses. This still does not attest OS-thread exit, unsupported GL
extension objects or complete native GPU retirement.

After releasing graphics locks, the worker obtains the second exclusive CPU
inventory. The inherited zero-callback requirement remains; do not waive it if
an owned homebrew run reports callbacks. Final admission rechecks current
pending/DMA state and both CPU acknowledgments under the graphics locks. The
actual current render context is checked again. Then all FIFO/graphics locks
are released for exclusive terminal-file publication on the original worker.
FIFO is reacquired afterward. Seal/error/deadline failures keep the attempt
quarantined. Only successful publication restores the previous FIFO halt state.

No BQL acquisition occurs while holding graphics locks. GL fences each have a
finite100ms wait; graph loops and buffers retain explicit capacities. File/GL
driver calls do not have individual cancellation guarantees, so the owned outer
process watchdog remains required. Queued CPU state cannot be freed on timeout.

finish274 and the old monitor seal269 cannot be combined: monitor sealing is
refused once an end actor exists. The new ready predicate only reads the already
armed observer's acquire-published state and immutable owner. It never resets,
revives or forces completion of observation. The terminal wire format and its
strict error-union decoder remain273.

The existing xwn-ledger265-report reports epoch1 initially and epoch2 after end
publication. Reports now include actual CPU acknowledgment thread IDs, epochs,
times, deadline, counts, native-context match, fence results and seal state.
The controller must save the initial report before requesting the end actor.
The page setter accepts an explicit end274,N prefix for terminal pages; ordinary
N still selects the immutable initial graph. Pages advertise their actual epoch.
Cursor selection changes only monitor read state, not actor state or evidence.

For a qualifying control, independently compare both graphs and context rows,
actual CPU identities/epochs/times, sealed accounting and owned texture snapshots.
Keep the frontend closed between the two captures, then reopen once through its
existing one-shot flow. Do not infer resumed guest texture reuse from a desktop,
a sealed log, unchanged CPU bytes or host-invoked binder calls.
