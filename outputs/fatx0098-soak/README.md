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

Status: physical launch accepted at 2026-10-06 02:06:48 UTC; result pending.
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
