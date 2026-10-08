# Surface callback diagnostic

Reuse exact probe141, RAM0112 and pinned xemu. No driver, cache or callback policy
changes. A fresh owned child repeats three untimed 192x96 solids at top, x128 and
y160, then the unchanged 45-case workload and full cold audit. Previous kits closed.

Pin the actual copy routine, operands and all96 row translations as before. Enable
only nv2a_pgraph_surface_cpu_read/write from upload entry to paired return. Disable
at EVERY debugger stop before reading guest memory; re-enable only when resuming
within the upload. HMP verifies state transitions. CPU-stopped prelaunch toggle
checks actual binary support; source/backend pins document synchronous log flushing.
Retain exact log byte windows and hashes; correlate surface base+offset to captured
physical source/destination ranges, reporting unrelated callbacks separately.

Limits: one upload per marker,64 stops/600 seconds,30seconds per trace segment,
4MiB per segment/16MiB total/65536 selected records. Running receive timeout checks
size/time every2seconds; this is a detection bound, not an OS quota. Overshoot is
failure and must still disable events and remove breakpoints. No speed claim from
this paused/instrumented run; no automatic callback disabling as a performance fix.
Presence proves overlap, not download waits or exclusive causality. Absence is
limited to these selected windows and trace points. Preserve all failed evidence.
