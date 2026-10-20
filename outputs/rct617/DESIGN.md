# PC617 continuously running timing control

Fresh404 original-only fixture. No retail or physical console access.
Keep616 counter primitives, process PID/creation/path verification, debugger
core, phase state machine and resource bounds. The subject now continues
pixel-checked copies after READY without waiting for GO. It exits only after
the controller releases it, or its512-copy bound fails. Both direct and traced
cases have the same paced work and twenty-second measurement.

The reusable window.h records start counters and COM1 marker before signaling
the recorder phase request. It polls acknowledgement while sampling; it never
suspends the subject or treats acknowledgement as a pause. Log request-call
before/after ticks and first observed acknowledgement outside the interval.
At the end record all counters and marker before writing any sample rows.

The recorder buffers every API11 entry tick (4096 per phase, unchanged hit
bound) and dumps those ticks after subject exit. Recorded pairs remain32 per
phase. Host review checks both sampled returns and every buffered entry,
separates ticks equal to interval endpoints, and never calls the count FPS.
All phase1 sampled calls must be strictly before interval end; timestamps
must prove the phase request followed the start counters. Initial and final
extra calls are measured facts rather than assumed absent.

The test remains too small and paced to quantify recorder overhead. Its purpose
is to qualify the reusable timing window and all-hit bookkeeping for the actual
RCT saved-scene comparison. Require normal shutdown, cold review and exact pins.
