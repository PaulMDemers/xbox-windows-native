**First emulator audit did not qualify.** Both graphics workloads, dashboard
returns and normal shutdowns completed, but new informational rundll32 popups
reported initialization during window-station shutdown. The strict audit remains
false. A new fixture with the identical driver and a 30-second pause before restart
is in ../video-trace-reuse-settled; its reports and the later strict passing clean-start series record the outcome.
No physical deployment was performed from this directory.

# Reuse the video trace across boots

Candidate 0092 removed file logging and diagnostic PCI reads. It passed two owned
emulator boots but failed on hardware with STOP 0xB4 before the workload. The exact
cause was not isolated. It was collected and rolled back; no second physical
cycle was launched. Its evidence remains in ../video-repeat-boot.

Candidate 0093 is a separate baseline-derived change. It preserves original file
open/read/write/close behavior, PCI reads, PnP callbacks and geometry. After the
existing file-length and marker checks, it clears the previous records in RAM
instead of stopping on them. Subsequent trace writes follow the original path.
The opt-in XBOX_NT5_VIDEO_TRACE_REUSE=ON selects this behavior; default OFF retains
the historical diagnostic guard. Missing/wrong-size/wrong-marker files and I/O
failures still stop explicitly. This enables reuse of a valid installed trace;
it is not a claim that the driver no longer uses or requires that file.

Source tree:329a29d61af1620a9fc005b0d8fcfb9e1a937d20.
Miniport SHA256:3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf.
The exact base, ordered patches, compiler hashes and video definitions are pinned
in inputs.json/manifest.json. build.py reconstructs in a fresh output under the
build lease and checks host backing-volume space. It does not deploy or launch.
The captured 0.1.0 tag, inputs and recovery package are unchanged.

Compiled-driver tests check trace/PnP behavior, existing error guards, elevated-
IRQL handling, unload/close and a populated file: a new boot's records start from
zero and the stale tail is cleared. Actual NT5 imports resolve. Geometry and PnP
source files are byte-identical to the qualified baseline. The emulator protocol
uses two exclusive workload logs, the same populated trace, and no host file
writes between Windows boots. Each run must pass four pixel checks, five timing
loops and normal restart. Cold audit requires both shutdown records and valid
current trace contents. Emulator results are separate from physical qualification.

Physical deployment is gated by that audit and exact baseline hashes. Old driver,
startup, trace and event logs are preserved; the verified remote rollback copy is
/F/winnt/system32/drivers/xboxvnt5.trace011. Fresh helpers use xwnrps01/xwnrps02.
Cycle 2 is gated by cycle 1 qualification, restores/reinstalls only test startup,
and verifies the trace still matches the cycle 1 collection before launch. No host
reseed is performed. Collection restores ordinary startup first and checks the
candidate/rollback/core binaries, helper hashes, fresh workload results, normal
shutdown, valid trace records and the new event-log boundary. Exact state is in
physical.json. rollback restores the baseline and a clean diagnostic seed without
launching Windows; preserve every failed attempt and never repeat a launch ID.

These bounded drawing tests do not qualify GPU acceleration, new modes, extended
storage/network workloads or electrical power-off. This change is boot maintenance,
not a rendering optimization. See audit.json and physical-cycle*-qualification.json
for actual outcomes rather than treating a visible desktop or FTP return as PASS.

Follow-up protocol: video-trace-reuse-clean-start passes a full strict two-boot
emulator audit, beginning with a clean seed and reusing its own first-boot output.
The physical trial lives in ../video-trace-reuse-settled; its reports are the
sole source for actual physical state. Earlier strict popup failures remain.
