# Post-0.1.0 video work

The [plan](PLAN.md) separates baseline measurement, mapping/cache review,
software/GPU drawing paths and video-mode handoff. No new video driver has
been installed on the physical Xbox. Its 0.1.0 hashes remain the reference.

Current result: [probe v3](probe-v3/README.md) fixes startup-window occlusion and
passes all four correctness stages with normal restart and cold log verification.
The earlier failures below are retained evidence. A separate physical baseline
trial `physical-gdi-001` did not exercise Windows: the user reported a keyboard
hang in Xromwell, unplugged it and rebooted. Collection restored startup and
found unchanged event logs with no probe attempt. The authorized retry lives in
`physical-gdi-002`; it was accepted but has not returned within the four-minute
observation. Screen state and collection remain pending. No physical timing or
new video-driver qualification is claimed.

`gdi-probe.c` is the first implementation. Build with `Build-Probe.ps1` using
the existing RosBE cross compiler. It uses only imports found in the captured
physical NT5 DLLs; `probe-build-review.json` records the binary/source hashes.
There is no dependency on a newer C runtime. Initial linking exposed implicit
memset calls; explicit zeroing removed that unwanted runtime dependency.

The probe creates a small topmost window, logs mode/capability data, verifies
right/down and left/up overlapping copies against a known RGB pattern, and
times five operations. It calls GdiFlush per operation, uses batch limit one,
caps each case at 2,000 operations or approximately 1.5 seconds between calls,
and supports Escape cancellation. A hung GDI call can still block; this is not
a watchdog. It never switches modes, edits drivers or reboots by itself.
The timings include message checks and synchronization, not pure memory bandwidth.

Timing kind 0 is opaque fill; 1 is DIB-to-screen; 2 is screen-to-DIB; 3 is
overlapping screen copy right/down; 4 is overlapping screen copy left/up.
All use 256x128 pixels. Correctness comparisons ignore the unused alpha byte.
Emulator wall-clock/guest timings are not physical throughput measurements.

Run it from a fresh owned directory: `gdi-baseline.txt` uses CREATE_NEW and a
second invocation will refuse to overwrite the first result. An isolated xemu
fixture places it under the historical helper filename `xwnpaint/replay.exe`
and uses the existing one-shot runner to request a normal restart only on
successful exit. This is an emulator harness convention, not a physical upload.
The preexisting qualified fixture remains hash-checked and unchanged.

`prepare-emulator.py`, `Run-Probe.ps1` and `audit-emulator.py` record fixture,
run and cold-read evidence separately. The first run is `nt5-gdi-baseline-001`;
do not repeat its launch record. A runtime failure belongs in a new retained
report, not a rewrite of a successful older Paint test. Review events and normal
dashboard return as well as the probe's PASS marker before qualification.

## First emulator result: probe not qualified

`nt5-gdi-baseline-001` reached the desktop and completed all five timed loops,
but both pixel-verification cases returned false. The runner correctly recorded
FAIL_REPLAY_EXIT and did not request an automatic restart. These results do not
yet distinguish GDI/driver behavior from an invalid window/readback assumption
in the new probe. Do not present the recorded emulated timings as a valid
performance baseline or compare them with physical window dragging.

A manual guest restart was requested through the Windows shutdown dialog after
reading the log in Notepad. The cold system log ends with EventLog6006; the
dashboard FTP return was not verified before the owned emulator was closed.
The cold probe logs are complete and both driver hashes are unchanged. The
system log also records HID7000, Ftdisk49, kbdhid1 and a shutdown rundll32 popup.
Historical delayed-write records earlier in that EVT belong to older fixtures.
No full-volume audit or physical Windows launch was performed in this test.

Next refine the probe to test DIB-to-DIB first, direct upload/readback second,
then overlap in each direction, recording API stage, first mismatch coordinates
and actual/expected RGB. Use a dedicated window class and wait for a settled
desktop; preserve screenshots to rule out occlusion. Qualify the measurement
tool before changing framebuffer mappings, hooks or GPU state. The failure is
retained as `emulator-audit.json`, not silently replaced by a passing report.
