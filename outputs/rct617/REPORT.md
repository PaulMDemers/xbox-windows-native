# PC617 closed PASS: timing a continuously running subject

Fresh404 original-only fixture ran19:06:01–19:09:30UTC2026-10-20.
Direct and traced subjects kept copying and checking pixels while the observer
started, timed and ended its window. They stopped only after the observer wrote
its buffered samples and signaled release. Neither subject was paused at a
phase acknowledgement.

Direct window20.016s ticks/20.015287s host; traced20.031s/20.017518s.
Both had183 process samples. Same-boot5s sleep matched4.999882s host.
QPC remained wrong and diagnostic only. Subject and tracer CPU increments were
zero at coarse accounting resolution; traced observer recorded0.015625s.
These small paced workloads do not estimate retail overhead.

Direct207 copies and traced218 copies passed every pixel check. The recorder
counted36 phase0 and182 phase1 entries.160 entry ticks were strictly inside the
measured interval, with5 at ambiguous boundary ticks; other entries occurred
outside it. All32 phase1 sampled call/return pairs were inside. The first
observed acknowledgement was109ms after request. Post-window entries were
real: the subject continued during buffered-log writes, so total phase hits
must not be substituted for measured-window counts.

The reusable window.h and timing.h now qualify this coordination for retail:
start counters/host marker before phase request, nonblocking acknowledgement
polling, separate process handles and bounded per-entry ticks. They neither
suspend the game nor infer timestamps. Recorded calls remain capped32 per
phase; breakpoint entry processing continues afterwards.

Normal shutdown, one new6006,6492 files/310 directories, five clean hives,
exact three tools and unchanged protected OS/seed passed cold review. All owned
processes are closed.22 host rejections and sanitized shared timing bounds passed.
Initial host setup failed before compilation because its parent directory was
absent;host002 corrected setup. Initial capacity admission failed before child
allocation. Both failures remain. Closed615 raw leaf was losslessly archived
with full roundtrip hash verification before removal; see archive001.json.

No retail or physical console launched in617. Next is618's matched retail
saved-scene measurement, gated on this actual result. No FPS, acceleration,
Xbox throughput or release promotion follows from this control.
