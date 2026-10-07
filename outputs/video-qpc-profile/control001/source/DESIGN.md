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
