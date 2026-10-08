# CPU framebuffer writes overlap an xemu GPU surface

The bounded diagnostic captured a concrete position-dependent emulator path.
The two 192×96 solid uploads at (0,0) and (128,0) generated no selected surface CPU
events. The same-size upload at (0,160) generated 17,280 write events, all mapped to
its framebuffer destination and one GPU surface with base 0x03c64000. Exactly 192
distinct four-byte start addresses occur on each of 90 rows (y160..249); the last
six rows (y250..255) have no selected callback events. No selected source-read or
unrelated-address events occurred. The trace does not expose the surface's size,
creation time or dirty/download state.

This is diagnostic evidence of callback overlap, not a speed measurement. The
earlier ordinary video-transfer-position run measured a 48× median difference
between top and lower solids; do not transfer that timing qualification to this
paused/logged run or to physical hardware. Existing source shows a callback locks
PGRAPH and traverses surfaces on CPU access; dirty surfaces can require download.
Actual lock duration/download activity and exclusive causality remain unmeasured.

## Capture and identity

Reused exact probe 141, RAM0112 and xemu-resource-model executable. No driver,
emulator, guest cache, service or device-policy changes. The inherited reviewed
probe imports and payloads are retained in pe-review.json; no new compile occurred.
backend.json records binary -trace help and borrowed generated CONFIG_TRACE_LOG
source pins. Actual HMP event states were toggled on/off while the CPU was stopped
before the Windows launch. LOG backend writes to the existing -D cpu-trace.log;
generated qemu_log/unlock source documents per-call flushes.

Fifteen byte-delimited trace windows cover the three selected uploads, with both
CPU-access events disabled at each stop BEFORE debugger reads and re-enabled only
when continuing the upload. All 15 windows total 864,000 bytes / 17,280 events. All event
states ended disabled, all breakpoints removed and the guest resumed. Capture
ended 06:13:21.626520 UTC after the single 06:12:27.712974 UTC launch on October 8.
Raw windows are preserved privately under candidate001/artifacts/surface-windows;
the original run cpu-trace.log and each window are hash-pinned by the verifier.

The inherited observer captures 24 guest events / 15 relocated resident-code pins,
actual PDEV/paired returns and 96-row source/destination page mappings per sample.
Display-header E14 remains explicit: identity uses kernel loader name/base/size,
exact resident code and cold PE hash. This is not an effective PAT/MTRR audit.
First-row copies are 768 bytes with matching before/after content and complete
ECX/ESI/EDI progress; each whole upload increments one upload and 73,728 bytes.

## Validation

Final cold and diagnostic qualification **PASS**. All 45 cases, 13,271,040
compared pixels, 45 exact reference files and 45 exact observed RGB readbacks pass.
The workload issued 87,168 measured BitBlt calls. There was one normal shutdown
and dashboard return at 06:17:17.134302 UTC; owned emulator cleanup completed at
06:17:17.5353558 UTC. Full allocation: 327 directories, 6,851 files and 328 directory
clusters, with zero errors/orphans. All five hives parse, protected hashes match,
and startup, configuration and the 96 MiB/1,536-cluster pagefile are unchanged.
Strict event deltas contain no warning/error or application events.

Both trace verifiers pass, including independent byte-window checks against the
closed original log. Ordinary and timing qualification remain **FALSE** because
this was an instrumented debugger run. No physical qualification is claimed.
Preparation 33640, runner 27052, tracer 14325, supervisor 44922, cold audit 34665
and verifier 82865 are all CLOSED. No next fixture or running session exists.

Synthetic checks cover 754 geometry/oracle cases, eight protocol failure gates, six
parser/range checks and nine recorded-window/state/teardown mutations. The original
eight mapping/pairing corruption gates are also retained. No callback was disabled
to change emulation behavior; only trace emission was switched.

## Scope and next work

The selected windows support the CPU-access callback hypothesis for this emulator
position effect. They do not prove that 0x03c64000 is an obsolete dashboard surface.
Pin sparse lifecycle traces from emulator startup in a NEW child before choosing
a synchronization or handoff fix. See NEXT.md and lifecycle-followup.json.
Physical 0101/video0093, the 0088 rollback, immutable 0.1.0 and all failed prior attempts
remain unchanged. No physical FTP, deployment or test was performed.

The first host preparation invocation failed PowerShell parameter conversion
before executing preparation; the corrected existing helper ran once (session 33640).
No fixture/guest retry occurred. This host failure is unrelated to guest results.
