# Next display diagnostic: elapsed engine and upload body time

Current112/167 counters show one128KiB upload for19/20 physical writer intervals
and zero uploads in3/5 readback intervals. Background hook activity remains in
other intervals. Bulk upload already compiles to REP MOVSL per row. Do not claim
the engine or framebuffer memory is the bottleneck from these counts alone.

Actual captured Win32k exposes VOID APIENTRY pointer-output
EngQueryPerformanceCounter and EngQueryPerformanceFrequency; both call the
actual KeQueryPerformanceCounter import. Matching owned DDK agrees. Runtime
frequency, monotonicity and measurement overhead remain unverified.

A new isolated113 diagnostic should preserve rendering, upload rectangles,
memory/cache type, owner selection, clipping and failure semantics. It should
add a separate versioned timing escape, retaining existing112 counter layout
for comparison. Read timing snapshots OUTSIDE timed loops. Report frequency,
back-to-back clock overhead/range, disabled/invalid/overflow states and actual
call counts. Never silently replace an unavailable timer with guessed ticks.

Measure EngBitBlt/EngCopyBits elapsed body time and upload copy-body elapsed time
separately, plus the complete upload wrapper if clipping/enumeration overhead
needs separation. These are elapsed times, including preemption/interrupts;
they are not exclusive CPU cycles. Keep unrelated background hook counts and
do not attribute them to the helper without a runtime discriminator. Confirm
display serialization or use an explicit safe snapshot/counter synchronization
contract before claiming atomic64bit totals on32bit NT5.

Meaningful validation: matched fresh ordinary control/candidate, identical
workload and source/binary pins; timer calibration; independent expected black,
white, pattern/DIB pixels plus existing copy/overlap/coherence; counter coverage
and overflow guards; full cold allocation/hives/protected/event audit. Compare
profiling overhead against control before interpreting body totals. Debugger
measurements cannot qualify performance. A clean future physical eligibility
screen must reject every Application Popup type, preserve Ft49 strict failure
and keep the actual physical baseline/rollback intact.

No timing driver built in168/169. No store/ROP/clip/mode optimization justified
until measured evidence identifies the limiting body. The recurring shutdown
installer popup remains a separate lifecycle investigation; no arbitrary waits,
service disabling, dialog cancellation or device-policy suppression to force PASS.
