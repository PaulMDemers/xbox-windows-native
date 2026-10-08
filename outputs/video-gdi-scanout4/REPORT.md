# Probe startup explained; no rendering qualification

Fresh diagnostic observed the real probe create result.log successfully, then
exit with code10 before its first XwnGdiShot checkpoint.252resident pins include
full display text and actual probe/kernel32 entry sites. Foreign mobsync.exe API
hits were recorded/stepped without treating them as probe calls. Real page-fault
entry deferrals, thread/frame pairing, full teardown and resume are preserved.

After the failed probe exited, explicit emulator keyboard input selected Restart
in the visible Windows shutdown dialog. This assisted cleanup is recorded in
manual-shutdown.json, not attributed to the workload. Normal shutdown1/dashboard
return recovered result.log: HARNESS_FAILURE0/error8 before any case records.
Error8 alone may be stale; it does not prove memory exhaustion or a driver defect.

Cold integrity PASS:325dirs6759files326directoryclusters, no errors/orphans,
5 structural hives and protected/payload hashes. A new kbdhid warning1 is retained
as strict failure, alongside the incomplete workload. No framebuffer cases were
captured; ordinary/physical qualification false. Never relaunch/recollect.

New video-gdi-coverage2 probe records exact failure stage/clip/stats, flushes each
record and requests normal restart even on harness failure. Same driver/rendering
cases and unchanged qualification gates. All original failures remain preserved.
