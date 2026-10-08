# Surface lifetime diagnostic

Reuse the exact probe141, RAM0112 and pinned xemu binary. Preserve all closed prior
cases. A fresh fixture enables seven sparse lifecycle events from xemu startup:
create color/zeta, invalidation, eviction reason/overlap, upload and download.
CPU-access events remain restricted to the same three bounded upload windows.

Capture the log offset before/after the one FTP launch request and at each actual
guest marker. These ordered byte intervals distinguish prelaunch surfaces from
later creations without inferring that a hostname, wall clock or screen implies
the executing guest component. Pin actual guest code/operands/page mappings.

All lifecycle tracing stops at the final marker, even on failure. Keep 16 MiB log
and 65,536 lifecycle-record bounds; the owned runner checks size each loop and the
observer checks during waits/markers. These are bounded detection, not OS quotas;
an overshoot fails qualification. CPU trace retains its separate per-window bound.
Keep full teardown and cold workload verification; no debugger timing qualification.

Infer a surface lifetime only from a recorded creation followed by no invalidation
or replacement before the observed callback. A creation event gives geometry and
pitch; exact extent inference must match pinned source size calculation and any
recorded bytes-per-pixel. Download events prove copies, not wait durations.
No event is a substitute for proving dirty flags or exact renderer lock cost.

Do not reset/flush the GPU, remove callbacks, modify caches or alter driver policy.
Establish the synchronization/handoff contract before choosing a change. Hardware,
physical0101/video0093,0088 rollback and immutable0.1.0 remain untouched.
