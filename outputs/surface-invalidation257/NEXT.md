# Next discriminator: controlled contents at the actual removal paths

All257 sessions are closed. Never relaunch or recollect preserve001. Inspect
final-review.json and the separate host failure/corrected-analysis records.

The new evidence narrows the next test to age eviction and CPU-write eviction.
Do not repeat the same scalar run or focus on flush alone: it had no entries.
No defect in those download paths is established by257.

Before compiling another emulator, design a bounded opt-in renderer diagnostic
that creates an isolated surface with independently generated asymmetric pixels
and guard bytes. Run on the existing GL worker with confirmed context ownership;
preserve prior bindings and keep the test range disjoint from guest-owned ranges.
Do not reuse live guest framebuffer contents as the expected oracle. Exercise
the actual age/download/removal path and compare all resulting bytes, including
stride padding and format conversion, against the host-generated oracle.

The separate CPU-alias case must execute an actual guest CPU read and write, not
a host memcpy masquerading as callback coverage. Prove the blocked store resumes
after readback, then establish that its newer bytes survive subsequent eviction.
Require distinct patterns before GPU work and after the CPU store so stale
downloads cannot produce a false pass. Pair each access with the same callback
generation and surface range. If existing diagnostic admission cannot safely
reserve this range and exercise real alias operations, stop before launch and
implement that bounded test interface first. No native GPU ownership is granted.

Count coverage explicitly. Missing CPU read, dirty download, post-store check,
guard-byte comparison or teardown is a failed test, not optional evidence.
Keep negative controls for a deliberately wrong expected byte/stride and stale
GPU copy; no additional policy/driver changes or event-gate relaxation.

Use a new kit/attempt, review the actual source and lock order, retain20GiB free
build guard, freeze dependencies (including diagnostic.py), and qualify the
new telemetry grammar before launch. Full cold audit and owned process cleanup
remain required. The phase250 fixture is historical and predates integrated
audio004; do not describe it as a test of the current physical combined demo.
