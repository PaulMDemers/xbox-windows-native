# Pointer placement did not remove the measured copy cost

Both fresh ordinary cases are CLOSED and strict PASS. Each completed 54 timing
cases and 162 full RGB stages, exact visible-arrow state checks, automatic normal
restart/dashboard return, clean allocation (324 directories, 6755 files, 325
directory clusters, zero errors/orphans), five structural hives and protected
hashes. Configuration/pagefile stayed unchanged and warning/error/application
event deltas were empty. No debugger, host input or capture during either run.
See pair-review.json for source/fixture/closure pins and all samples.

Only startup cursor position differed: 512,288 intersects the large copied region;
820,460 is outside the largest copied rectangle but inside the same client.
Both use the identical probe109 and explicit visible standard arrow. All drivers,
mode, registry and inherited emulator-only device policy remain identical.

Large 768x384 median elapsed milliseconds per operation (three rotated rounds):

|Path|Pointer inside|Pointer outside|
|---|---:|---:|
|Fill|66.00|66.00|
|Upload|66.00|66.00|
|Readback|7.14|6.98|
|Screen overlap|72.00|72.00|
|RAM overlap then upload|66.00|69.00|
|RAM overlap only|0.55|0.56|

These shared-slot functional emulator timings include operation, GdiFlush, message
pumping, visibility and cursor checks. GetTickCount resolution and one run per
position limit precision. No physical throughput/FPS or isolated bandwidth claim.
The equal dominant medians do not support pointer placement as the dominant
source of the measured cost. They do not prove that pointer work is free.

The earlier video-transfer-observed trace independently captured additional
small surfaces/copies around the pointer. That debugger evidence remains separate
from ordinary timing. The next discriminator is calibrated QPC brackets around
operation, flush and loop checks, or resident-pinned capture of the actual
row-copy branch; no speculative renderer/cache patch follows this negative test.

Earlier video-cursor-profile/outside001 remains failed before timing, manually
inspected/restarted and unqualified. Its exact failed predicate was not logged;
this successful within-client comparison does not retroactively prove its cause.
trace001 E14 and trace002 never-launched preparation failures also remain intact.
No physical access or hardware change.
