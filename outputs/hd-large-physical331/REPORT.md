# Physical large-area run closed: workload passed, combined qualification failed

One Windows launch was accepted at 03:51:48.621670 UTC on October 13, 2026;
dashboard return was observed at 04:00:01 UTC. All five samples completed all
15 large-area cases at 256x128, 640x360 and 960x540, including independent pixel,
source and guard checks. Legacy drawing, text and window checks, six audio API
phases, installed audio bindings, setup-idle checks and normal shutdown passed.
Actual mode was 1920x1080x32, pitch7680. This run has no new user screen or
audibility observation.

The original combined-event gate FAILED: Srv2013 for Windows F: occurred
inside the measurement interval. The inherited Ftdisk49 event also remains a
strict whole-boot failure. There were no application events or shutdown popups;
one EventLog6006 confirms normal shutdown. Both scoped_combined_passed and
strict_qualification_passed are FALSE. The pass-gated summarize.py was not run,
and no qualified measurement-summary.json was created.

Read-only failure-review.json preserves the failed verdict and pins the exact
source records. The owned historical NT5 message resource identifies Srv2013
as an at-or-near-capacity warning. Both newly captured SYSTEM hives map Windows
F: to byte offset2359820288, exactly matching the historical dashboard C:
system-partition mapping. This is unrelated to host C:/E: cleanup. No current
space API query or independent allocation scan of that small partition was
performed; historical free-space measurements do not establish current space
or a driver cause. No console files or alert thresholds were changed.

## Integrity and restoration

Collection restored normal startup first, preserved all six actual HD payloads,
then restored and readback-verified all six incoming baseline files. One owned
read-only allocation scan at /E/Applications/XWNHD331scan completed and returned.
It reports6227 directories,122692 files,6232 directory clusters, zero orphaned
clusters and zero errors. All five hives passed structural checks; selected
policies, device bindings, event history, protected payloads and SetupAPI history
passed their original gates. The final fresh FTP readback again verified normal
startup and baseline files. The historical video trace was unchanged; its shared
allocation entries are not fresh observations from this boot.

The physical installation remains audio004/softwarevideo118/shared158/FATX0101.
No rendering optimization, registry change, device disabling or permanent HD
deployment was made. All owned sessions are closed: Windows observer97226,
collection43115, scan observer99137 and audit47900. Never relaunch or recollect
physical001 or its scan. Frozen1303 inputs remained exact. The complete capture
count and hashes are in final-review.json and physical001/private-artifacts.json.

## Diagnostic timings from this failed combined trial

These are medians of five samples within ONE boot, not independent boots,
desktop frame rates or a qualified performance comparison. GDI flush, message
dispatch and visibility checks are timed; pixel/source/guard oracles and
statistics reads are outside timing. No driver changed between these samples.

| Operation | 256x128 ms/op | 640x360 ms/op | 960x540 ms/op |
| --- | ---: | ---: | ---: |
| Fill | 1.861 | 14.151 | 31.875 |
| RAM upload | 2.698 | 18.750 | 41.667 |
| Overlap down/right | 2.022 | 17.386 | 40.263 |
| Overlap up/left | 2.294 | 17.857 | 40.263 |
| WM_PAINT | 2.809 | 18.659 | 41.667 |

The large operations take substantially longer, but this does not locate the
cost within GDI, RAM drawing, copying or synchronization. Do not promote an
uncached-store or GPU change from these aggregate numbers. The earlier matched
209 scalar-store experiment found no hardware benefit and remains separate.

Recovery329 and emulator330 remain independently qualified within their stated
scopes. Immutable0.1.0/0.2.0 tags and recovered archives are unchanged. The current
private package is E:/Codex-archive/xbox-windows-native/0.2.0-recovered329, with
START-HERE.md for installation and rollback instructions.
