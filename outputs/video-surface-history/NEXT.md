# Next: a synchronization regression before changing watch lifetime

Read REPORT.md, OPTIMIZATION-DESIGN.md, lifecycle-verification.json,
surface-verification.json and trace-verification.json. This candidate is CLOSED, diagnostic/cold PASS. Never
relaunch/recollect this candidate or older closed attempts.

Runtime now identifies the retained watch: prelaunch 640Ã—480 ZETA surface,
pitch1280/BPP2, extent [0x03c64000,0x03cfa000). It is downloaded during handoff but
not invalidated before the measured Windows uploads. Its extent exactly predicts
zero/zero/17280 callbacks for the three rectangles. There are no GPU transfers in
those upload windows. This is stronger than the earlier overlap-only evidence,
but does not prove an unobserved reset contract or measure exact callback cost.

Next build an owned, bounded GPU/CPU coherence regression covering GPU-write/CPU-read,
partial CPU overwrite, repeated CPU stores, GPU consumption of those stores, and
another GPU-write/CPU-read cycle, followed by invalidation/reset/shutdown. Require
exact bytes for color and depth surfaces, actual coverage and pinned dependencies.
Use the existing Xbox toolchain/leases and a NEW fixture. Do not use the physical
console or alter its drivers. Do not reuse these NT5 attempts as mutable fixtures.

Then design a CPU-authoritative watch state that avoids repeated callback work,
with safe deferred removal/rearm and in-flight callback ownership. Static source
shows async CPU operations and synchronized TLB flushes; immediate list removal or
free from inside a callback is not justified. Existing DIRTY_MEMORY_NV2A has other
consumers, including vertex-buffer code. See the design's validation obligations.

Only after coherence regressions pass should a matched ordinary candidate use the
existing position/transfer and real-window benchmarks. Keep debugger and performance
qualifications separate. No blanket callback disable, GPU reset, event suppression
or framebuffer relocation merely to force faster results.

Preserve physical0101/video0093,0088 rollback,immutable0.1.0, all failures and the
20GiB build guard. Check current capacity before any new build or fixture; it is
close to the guard. All existing backing chains must remain valid.
