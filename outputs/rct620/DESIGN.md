# PC620 instruction-location sampling qualification

Original workloads only: sleeping, arithmetic loop, memory copy and GDI copy.
Compare each workload with and without bounded main-thread snapshots. No game,
console, kernel/driver modification or closed-runtime reuse. Fresh immutable404
fixture only after host tests, exact compiled media and capacity admission.

Sampler owns one SuspendThread increment and always attempts one ResumeThread,
including GetThreadContext failure. Reject a preexisting suspension, unexpected
resume count, exited thread, invalid CS or missing executable location. No I/O,
heap work, other-process counters or module enumeration while held. Buffer at
most512 samples, jitter50â€“113ms, stop after20s. Record suspension duration and
actual process/thread CPU time; readback process identity and module bounds.

A snapshot is an observed saved user instruction location, not automatically a
CPU-time profile or kernel stack. Controls must show sleeping low CPU and busy
high CPU, and observed busy/copy locations in their independently exported
assembly ranges. GDI may sit in ntdll syscall return stubs: leave that unresolved,
not classified as sleeping or game work. Inspect same-module stability and
unobserved/observed costs before any retail sampling. Counter resolution and
single-CPU scheduler bias remain explicit limitations. Do not sum snapshots into
FPS or kernel-time attribution.

Require normal subject exit, exact workload results, normal restart and cold
file/hive/OS/seed checks. Keep failures and artifacts; never overwrite a failed
attempt. Physical720p/launcher/packages and paused automation stay unchanged.
