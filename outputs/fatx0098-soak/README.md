# FATX0098 timed hardware soak

Keep the qualified FATX0098 filesystem and video0093 unchanged. This attempt
uses C:\xwns98 (dashboard F:) and an exclusive result log. No raw storage write,
trace reseeding, driver update or display-mode change is part of this test.

The helper first replays 16 BMP save sequences recorded during earlier Paint
diagnosis, using a deterministic 512x288 scribble. This is API replay, not Paint
UI automation. It then creates 17 boundary-sized inputs and performs 15 rounds
of output write/flush/reopen/mapping plus copy/rename/mapping/delete. Expected
mapping count: 527. Physical rounds finish no earlier than one minute apart,
so the workload lasts at least 15 minutes before requesting a normal reboot.
Rehearsal uses the exact same executable with the explicit `rehearsal` argument
and four-second intervals (at least one minute), which does not qualify the
physical fifteen-minute duration. Actual Paint/Notepad observations are separate.

Build.ps1 and the two review JSON files pin source, compiler, executable hashes
and Windows 2000 imports. prepare.py creates a new owned xemu child; Run.ps1 and
supervise.py own its single launch and cleanup. The cold audit verifies the exact
50 final test files, all 34 deleted intermediate paths, timing markers, events,
payloads and hives. Previous fixtures and failed attempts remain preserved.

physical.py reads the installed baseline, stages only owned helper files and
one-shot startup, and records a single launch. It will not repeat an existing
attempt. collect restores ordinary startup first, then preserves files, logs
and before/after trace bytes. restore-startup performs no launch or driver write.
The old0088 rollback remains at F:\xwneof98\rollback.sys; this attempt separately
preserves its unchanged0098 starting driver. FTP credentials come from environment.

After return, use the owned read-only scan once, collect, audit all 3,439 manifest
binaries and nine registry hives, then qualify.py and final-state.py. A PASS log
or dashboard return alone is insufficient. Never relaunch this test after a
launch timeout. Keep manual application results separate from automated checks.

Status: physical run returned after user restart; timed soak incomplete. See summary.json and the result below.
Emulator storage/allocation checks pass, but the known shutdown popup remains
a strict emulator failure; eligibility.json preserves the bounded decision. Release0.1.0 is
unchanged. No video performance, HD modes or general concurrency claims follow.

## Collection and recovery

The observer only checks for dashboard return; it never launches another test.
On return, collect restores startup before reading results. audit-manual.py
checks the optional suggested BMP/text files without asserting actual UI success.
Keep user observations separate. The hardware qualifier also rejects the shorter
rehearsal interval; six negative verifier cases exercise missing/corrupt outputs,
leftover copies, truncated completion, missing replay results and short duration.

capture-recovery.py may run only after qualification and final-state PASS.
It creates a fresh private snapshot under
E:/Codex-archive/xbox-windows-native/fatx0098-video0093-20261006, capturing the boot
application, Windows, profiles, Program Files, selected owned test directories
and root evidence, plus current dashboard/config. It excludes games, unrelated
applications, pagefile and firmware. Every ZIP file entry is read back and hashed.
A resumed capture requires the startup/SYSTEM/SOFTWARE/event-log fingerprint to
remain unchanged. This is a file-level snapshot; a full restore is not tested.
The original version0.1.0 archives and tag are not modified.

## Collected result: interrupted timer, clean observed storage and integrity

The user reported restarting; dashboard return was observed at02:23:36UTC.
All527 mapping checks completed with zero content/tail failures,16 synthetic BMP
save sequences passed, all50 final automated files match, and all34 intermediate
paths are absent. Only14 timed completion markers were written; the last reports
840000ms. The final900000ms marker, COMPLETE and automatic restart request are
absent. This is not a full fifteen-minute pass, and it is not a demonstrated
driver failure. The strict qualification remains false.

Normal event-log shutdown is present; no application events or popups were added.
Three Srv2013 warnings exactly match earlier records (warning-comparison.json),
and remain in the strict result. Post-return allocation is consistent across
122248 files/6069 directories with zero orphans/errors. All3439 binaries and nine
structural hive audits pass. installed-state.json confirms normal startup,0098/
0093 baseline hashes and the original0088 rollback. No further Windows run or
PASS-gated recovery capture occurred. The original0.1.0 archives remain intact.

The user's files used different names: manual-apint.bmp and manuel-note.txt in
C:\xwns98. Both were collected; the961x532 RGB bitmap decodes fully and the text
contains27 ASCII bytes. Their hashes are in manual-discovered-audit.json.
This preserves the original suggested-name audit, which correctly found those
suggested names absent. Application/UI observations remain user-reported;
synthetic save replay and cold file checks do not prove hardware acceleration
or a measured window-drag speedup.
