# Large-copy time is inside BitBlt

Both revised ordinary cases are CLOSED and strict PASS:54 cases and162 full RGB
stages each, exact timed/post cursor checks, automatic normal shutdown/dashboard
return, clean full allocation (324 directories,6755 files,325 directory clusters,
zero errors/orphans), five structural hives and protected hashes. Configuration
and96MiB pagefile map stayed unchanged; no warning/error/application event delta.
No debugger, host UI or capture during either revised run.

Identical probe111/drivers/mode/policy/cursor position in fresh children; only the
startup instrumentation mode differs. Source/binary/backing/disk/metadata pins
are verified in pair-review.json. FATX0103/HAL0102/NVNet0104/ATAPI0105/video0093,
restored HidServ and inherited emulator-only null/unsupported-device policy are
unchanged. No physical access or hardware qualification.

768x384 medians, milliseconds per operation:

|Path|Control total|Detailed total|Drawing call|Flush|Loop checks|
|---|---:|---:|---:|---:|---:|
|fill|64.8700|71.5984|68.5134|0.0098|0.0523|
|upload|65.3451|66.2153|66.1476|0.0116|0.0459|
|readback|6.9379|6.8395|6.8141|0.0051|0.0168|
|screen_overlap|73.4965|72.3589|72.2980|0.0110|0.0434|
|memory_overlap_upload|68.4704|68.5572|68.4633|0.0140|0.0544|
|memory_overlap|0.5407|0.5459|0.5319|0.0035|0.0083|

Columns are independent medians across three rotated rounds; they need not sum
exactly. Each raw sample retains all sums and explicit unbracketed overhead.
In every large upload/overlap sample the drawing-call interval accounts for
99.8807%-99.9368% of the outer loop total (upload99.8977%-99.9198%). Thus flush
and loop checks are not the dominant measured cost for these operations.

The matching control/detailed large upload totals differ+1.33%, overlap-1.55%.
This does not establish universal negligible instrumentation effect: large fill
differs+10.37%, and the18 path/size median ratios span0.874-1.242. Scheduling,
measurement overhead and run variability remain; no driver or hardware speedup
is claimed. Functional shared-slot emulator elapsed time is not physical copy
bandwidth, isolated CPU time or window-drag FPS.

Counter qualification: stable1125000Hz, nonnegative/monotonic readings, bounded
intervals, checked64-bit sums,128 adjacent read pairs before/after each case.
Largest QPC/coarse-clock discrepancies14.16ms control and14.64ms detailed meet
the predefined max50ms/10percent gate. Large detailed adjacent-pair means span
about1.21-1.50us. These costs are retained, not subtracted as an exact correction.
Real logs pass; check-protocol.py rejects20 damaged protocols including overflow
words, zero frequency, missing records/completion, inconsistent calibration and
premature loops. These are host parser checks, separate from guest qualification.

The revised control needed10 readiness attempts/3840ms initially. The detailed
case needed one attempt for every case (maximum480ms). Same exact visible-arrow
identity/position checks50ms apart are required before timing; no timed gate was
relaxed. This records transient readiness, not the precise cursor handoff cause.

Earlier video-qpc-profile control001 passed, but instrumented001 failed before
any timing because actual cursor handle65575 differed from selected65553. It was
manually inspected/restarted, audited and remains unqualified. No mixed-binary
pairing or relaunch. All failed evidence and post-exit interventions are retained.

Next inspect the actual selected row-copy branch and framebuffer access in a new
bounded debugger child. Prior trace found dispatch at win32kRVA26e60 to117125;
its static possible callees do not identify the executed branch. Keep ordinary
timing separate from debugger evidence. No speculative cache/renderer patch.
