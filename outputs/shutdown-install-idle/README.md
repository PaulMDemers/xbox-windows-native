# Paired idle/restart installation test

Owned emulator fixtures only. Physical baseline FATX0098/video0093, original0088
rollback and immutable0.1.0 are preserved. No hardware access or automation.

## Design

001 is the original uninstalled rehearsal with only a common helper/startup edit.
002 is that same rehearsal with the previously verified GPU package staging and
DevicePath append, plus the identical helper/startup edit. Both wait120,000ms
from helper entry, write a small write-through timing log, enable shutdown
privilege, and request normal restart. No mapping, BMP or user application
workload runs. Windows still performs ordinary background I/O; this does not
disable storage or prove the installer process has exited. Timing is fixed.

The exact existing INF references installed framebuf.dll and copies only the
unchanged0093 miniport. No signing policy, FAILEDINSTALL flag or suppression is
added. Baseline driver/kernel/runtime identities are checked cold. This pair
changes workload/timing relative to the earlier60-second mapping experiment;
only the within-pair comparison isolates the package staging difference.

## Results, 6 October 2026

| Case | Package staged | Idle elapsed | Shutdown / dashboard | Popup | Result |
| --- | --- | --- | --- | --- | --- |
|001 control|No|120,000ms|Normal / returned|None|Bounded idle PASS|
|002 installation|Yes|120,000ms|Normal / returned|One rundll32 window-station shutdown error|Strict FAIL|

001 launched18:48:34 UTC, returned18:51:30.002 launched18:52:28, returned18:55:27.
Both were single launches with automatic guest restart. No debugger, capture,
manual dialog dismissal, forced reset or host timeout cleanup was needed.

Both cold audits confirm no original mapping/BMP workload logs, exact checked
payload/runtime binaries, five traversable hives and no other unexpected event
errors. Both F: allocation audits report zero orphans/errors. Control has321
directories/6,737 files; package has322/6,742. No full archive hash audit or other
partition qualification is claimed.

The control has no completed class-driver binding (ConfigFlags1024, Start1),
which is expected and not an idle-test failure. Package002 has ConfigFlags0,
class0001, exact oem2.inf, existing framebuf registration and Start3 set by
Windows. SetupAPI records successful full installation, query-remove veto6 /
CfgMgr32 code23 and reboot required. Successful install is not successful live
removal. No flags were changed offline to manufacture success.

The new error is the same text as earlier shutdown popups. No process/command-line
trace identifies its owner in this run. Do not assign it to the GPU or emulator
PCI1B36:0005 solely from the prior experiments. The explicit mapping/BMP workload
is not necessary to produce this failure, and the120-second idle interval did
not avoid it. Ordinary background Windows I/O still occurs. This one pair does
not prove the package always causes a popup or rule out other timing effects.

Next: use this smaller first-install reproducer to trace the hard-error process
identity and installer completion/shutdown ordering. Preserve normal boot traces
separately from debugger observations. Avoid simply increasing sleep intervals,
clearing failed-install flags or hiding errors. The three clean installed-state
replays and these first-install failures remain distinct; no hardware promotion.

All owned processes have finished. Pair/source consistency is checked by
verify-pair.py; its evidence_consistent result is not a test PASS. Raw private
artifacts and all earlier failures remain retained.

## Tools and evidence

Build.ps1/review.py pin compiler, flags, source, helper hash and owned NT5 imports.
prepare.py refuses existing fixtures; verifies source hashes and readback and
preserves SYSTEM/SOFTWARE/video trace during common helper staging. Existing
package metadata is identified as inherited, not a new common-stage hive edit.
Run.ps1 uses the owned emulator leases and unique disks; supervise.py launches
once on localhost4596. audit.py checks exact helper completion, absent old
workload logs, five hives, binaries, event deltas and dashboard return.
audit-package.py records registration and exact installed INF; a control without
the package is not expected to pass the installation-specific checks.
audit-allocation.py runs the established full F: allocation analyzer read-only.

Use WSL Ubuntu Python3 for disk/hive tools with LD_LIBRARY_PATH pointing to
/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu.
The supervisor consumes XWN_EMULATOR_FTP_USER/PASSWORD for127.0.0.1 only.
Do not repeat an accepted launch or rerun a completed allocation capture.
Raw Windows files/hives/disks remain ignored private artifacts.

A clean pair cannot alone establish a general popup fix, full PnP lifetime or
hardware qualification. Recurring identical SCM7000/Ftdisk49 baseline signatures
remain recorded; physical Srv2013 warnings and previous failures are not waived.
No debugger or live framebuffer capture is planned for these timed runs.
