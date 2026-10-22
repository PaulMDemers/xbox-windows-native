#648 CLOSED: validate elapsed polling time before changing mode setup

Read REPORT.md and actual user-observation/collection/audit/closure001. Second
amber/off after pause identifies wait3 (pair2 clear) in this instrumented run.
The first clear/set pair completed; no sampled-byte or elapsed-time receipt.
All28 selected files unchanged; no new Windows events. Original720p/startup
intact, no hook/rollback/owned process, isolated diagnostic files retained.
Never rerun/recollect648/647 or another closed runtime. No SITE queued.

Next independently inspect and test the exact compiled wait_us/GetTimerTicks
path from the retained build (no closed runtime involved). Current compiled
adapter/wrapper tests mock delay; do not assume100000 requested10us delays prove
one physical second. Model monotonic, wrapping and discontinuous timer input,
validate conversion/bounds and document timer-width/frequency assumptions. Inspect
floating-point prerequisites without altering FPU/control/interrupt state.
A host model cannot establish the physical timer or clock behavior.

Then design a NEW bounded diagnostic to report an elapsed-time category for the
failed poll and distinguish it from a sustained status value. Prefer recording
already-used timer values or explicitly reviewed read-only timer accesses; keep
video register reads/writes, predicates, limits, reset logic and protected720p
unchanged. Retain perturbation from added bookkeeping and LED timing explicitly.
Validate source, binary, model bounds and indicator decoding before any staging.
Use a new kit/build/owned E path, existing leases and exact preflight/readback.
A subsequent physical result needs a watched observation; no automatic rerun.

Do not increase timeout, clear pending bits, borrow firmware state, bypass a
validation gate or apply a speculative driver/profile change. If adequate elapsed
time is demonstrated, review the status source and scanout timing/clock readback
with primary evidence before selecting a functional experiment. No assertion yet
that scanout stopped, adapter failed, or timer is broken. No prior645 diagnosis,
boot fix, live-mode switch, other-revision or acceleration promotion.
Automation stays paused. Preserve every failed attempt and exact continuation.
