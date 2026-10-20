# PC615: paused saved-scene process-cost baseline

**CLOSED PASS; cleanup PASS.** Fresh immutable404 PC fixture, one direct,
uninstrumented RCT launch. No physical-console access. Run17:57:50–18:07:10UTC
on2026-10-20. No timeout, forced stop or screenshot error.

The exact PC593 saved park loaded after a deliberate camera move. All165600
scenery pixels matched the retained reference and stayed identical across the
measurement. Nine private captures were visually checked. Options show Window
mode; both boundary records show the same foreground game PID,640x480 client,
1024x768 desktop, origin and pointer position. The park was paused.

| Counter | Recorded result |
| --- | --- |
| Game interval, guest ticks |20.016s|
| Game interval, independent host |20.015898578s|
| Game process CPU |19.859375s,99.2175% of tick elapsed|
| Kernel / user CPU |6.921875s /12.9375s|
| Memory samples |174, bounded nominal100ms polling|
| Working set |35,319,808 bytes throughout,33.684MiB|
| PagefileUsage counter |56,569,856 bytes throughout,53.949MiB|
| Observer CPU increment |0 at coarse accounting resolution|
| Same-boot sleep check |5.000s ticks /5.001333517s host;0 CPU|

QPC remains unsuitable for elapsed time in this PC configuration: reported
frequency26,522,670,000 yielded0.715089s for the five-second sleep and2.863580s
for the game interval. No correction factor or driver change was introduced.
Host/tick agreement passed the unchanged max100ms-or5% gate.

RCT consumed almost the whole emulated CPU while the saved scenery stayed still.
This is a useful cost baseline, not proof of where that cost occurs. Busy polling,
simulation work and redraw costs have not been separated. Kernel/user accounting
does not identify an API. PagefileUsage does not measure paging traffic. The
observer's zero increment at15.625ms resolution is not proof of zero overhead.
There is one sample interval, no statistical variability bound, game FPS result,
Xbox throughput result, tracer-overhead comparison or acceleration claim.

The runner reads the actual game process handle returned by CreateProcess.
It samples memory in a bounded array, with no screenshots/file writes/input/window
calls inside the timed interval. Only the two bounded COM1 boundary markers are
written there. Automatic host screenshots stop at the first sleep marker, before
game launch. Counter/serial primitives are inherited from the qualified614
control; direct launch from603 and corrected load/reference checks from612.

Validation:13 cost/timestamp/source rejection cases,10 copy-contract rejection
cases and7 scene rejection cases; exact compiled source and PE/import checks;
503-asset media readback and guest verifier. The cold audit hashed7003 files/
315 directories, checked five clean hives and raw event chronology, and recorded
one new6006 normal shutdown. Temporary game registry restored, exact saved park,
tools, protected OS binaries and404 seed retained. Only the previously allowed
CSS0.DAT/Game.cfg game assets changed. All owned VM/reader/build/audit processes
are closed. Never reopen, recollect or parent this runtime.

Evidence: [cost review](cost-review001.json),
[raw counters](raw-counter-logs001.json), [host markers](serial-host001.json),
[scene review](scene-review001.json), [cold audit](ntfs-cold1-002.json),
[final closure](final001.json), [next steps](NEXT001.md).

Xbox unchanged: last dashboard/no owned hook;596 SOFTWARE cleanup remains
cold-only. Protected720p/ordinary launcher/saves/private packages unchanged;
packages still exclude RCT. Other-console, sound/fullscreen/input, boot and1080i
deferrals remain. Automation remains paused; no hardware action requested.
