# Calibrated NT5 GDI timing decomposition

One binary, fresh control001/instrumented001 children, environment mode0/1 only.
Both select the same visible arrow at820,460 within the client outside copied
areas.54 cases/162 full RGB checks, same fixed drivers/mode/device policy.

Control brackets the whole timed loop with QPC. Instrumented adds four QPC
reads per iteration delimiting operation, GdiFlush and message/visibility/cursor
checks. Raw unsigned64-bit ticks are serialized high/low; each query is checked
for success/nonnegative/monotonic values, intervals bounded30s, sums checked for
overflow. Frequency must be positive, stable and <=2^31-1. Before/after each
case128 adjacent query pairs measure min/max/summed instrumentation cost.
No guessed subtraction: raw costs and calibration are retained. The control
provides an instrumentation-perturbation comparison. Outer minus component sums
is explicit unbracketed bookkeeping/query overhead, not assigned to rendering.

Require QPC/coarse elapsed agreement within max50ms/10percent (coarse timer
quantization), completed bounded loops, exact pixels, cursor state, automatic
normal restart, cold allocation/hives/protected hashes/config/pagefile/events.
No host debugger/UI/capture during measurements; no parallel build/audit during
active timing. Functional emulator slot is not physical performance isolation.
No driver patch or speculative acceleration follows from timing alone.

## Bounded cursor readiness before measurement

Previous video-qpc-profile instrumented001 failed before timing: visible pointer
at820,460 but actual handle65575 differed from selected65553. Windows stayed
responsive; manual log inspection/restart and cold audit are separate failure
evidence. Do not relaunch/recollect or combine its control with this new binary.

New helper permits up to10s for the same exact cursor state and visible test
region to settle, pumping messages and selecting the same arrow at the same
position. Two matching checks50ms apart are required before every case; attempts
and wait milliseconds are logged. It neither accepts a different handle nor
hides the cursor. Timed/postcheck identity/position/visibility gates are unchanged.
No event or pixel gate relaxed; no dialogs automatically cancelled. Cause of
the earlier mismatch is not established. Both new modes share this readiness.
