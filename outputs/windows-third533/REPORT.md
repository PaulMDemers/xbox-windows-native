# One watched Windows success/failure/success sequence

The user's every-other-boot observation reproduced once in this finite sequence:

| Launch | Preceding state | User observation | Cold evidence |
| --- | --- | --- | --- |
|532 first,18:34:24UTC|Requested full power-off/on, dashboard|Windows desktop, then requested normal Restart|New6005/6009/6006; five clean hives|
|532 second,18:37:45UTC|Windows normal Restart, dashboard|Black screen, then dashboard|All ten collected files unchanged; no new event records|
|533 third,18:40:16UTC|Failed launch's dashboard return|Windows desktop, then requested normal Restart|New6005 and6006; five clean hives|

All three requests used the identical installed720p XWNEBoot executable and FTP
method. No intervening power cycle was reported, and no host file/trace reset,
temporary startup hook, driver or firmware change was made. Each request had
its own exclusive journal and one20second reply bound. First/second532 were
closed before the separately predeclared third533 request. No fourth launch.

Before the failed second and successful third, all ten collected file contents
were identical. The failed second did not change the selected launcher, normal
startup, registry hives, event logs or video trace. This is selected-file evidence,
not whole-disk equality. Both successful boots produced new Windows startup and
normal-shutdown records. Both also produced the known Ftdisk49 warning; strict
clean-event qualification remains false. No new application event records.

Third cold audit independently validates both before/after hive copies with the
existing two-reader/raw-value audit. System, software, SAM, security, default and
system event log changed on the third successful boot. The video trace remained
byte-identical across this successful boot, illustrating why unchanged trace
bytes alone cannot establish that no boot occurred. Events and user observation
supply the positive evidence. Event decoding scans validated records and may
include stale records outside the active ring; it does not establish completeness.

Interpretation: the state preceding each launch is a concrete discriminator to
investigate. This sequence is consistent with alternating behavior, but one
sequence cannot establish a deterministic rule or attribute it to caches,
interrupts, memory mappings, storage, USB or another component. Timing and
unmeasured console state remain uncontrolled. No functional fix was installed.

All533 host launch/collection processes and independent audit are closed. User
reported Rebooted after the requested normal Restart; dashboard readback then
authenticated. Ordinary startup/launcher/720p unchanged, no hook or cleanup owed,
no dashboardC access. Owned evidence retained; automation remains paused.
No new D3D/GPU/game/release or general boot-reliability qualification.

Read532 REPORT for the preserved prelaunch host-review failure: an extra-NUL
magic assertion failed but orchestration continued. Corrected review002 and the
separate presecond gate validated the existing16-byte marker before launch2.
That defect changed no console bytes and is not hidden as a clean initial gate.
