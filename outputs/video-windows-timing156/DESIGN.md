# Isolated emulator elapsed time for the reviewed watch optimization

The implementation is already present in xemu build003 and passes native
linear/swizzled/overlap/reset plus ordinary Windows155 correctness. This NEW pair
measures that emulator change with identical RAM0112 and compiled141 guest payloads.
It does not measure physical video-driver speed. No new guest/emulator source patch.

Prepare both fixtures, cold configuration/pagefile checks and source snapshots
before either run. Seal readiness. Run control then candidate under actual build
and exclusive xemu locks, checking lock conflicts before launch and after dashboard
return. Do no preparation, build, audit, screen/state capture or debugger work
during either workload. Audit both only after both runtimes close. The same bounded
FTP observer and sparse surface lifecycle tracing apply to both; CPU access events
remain off. ManualCapture disables the runner's periodic screen/state capture.

Require original45 functional cases, independent references/observed RGB, exact
counter relationships, three rotated repetitions, monotonic/stable QPC and coarse
clock agreement, quiet counters, normal shutdown/dashboard return, strict event
deltas, full allocation, five hives, protected/startup/config/pagefile checks.
Any failed gate prevents timing qualification; do not waive errors or relaunch.

Compare per-operation QPC medians/min/max for all15 geometries and both primary
and memory paths. Highlight equal-area top/top-offset/bottom cells: predicted
depth-watch overlap0/0/17280 pixels. Retain raw loop/calibration counts and clocks;
whole boot/runtime and independently calibrated total-call counts are not speed
ratios. Three within-run repeats and one run per build are limited sampling,
with control-first order and uncontrolled OS background activity. Cooperative
resource isolation is not exclusive host scheduling or physical throughput/FPS.
