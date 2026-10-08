# Actual installer lifecycle captured; prior popup unresolved

ONE fresh launch accepted2026-10-08 23:41:41 UTC; normal restart/dashboard and
owned runner42522/tracer8350/supervisor92673/cold audit5047 all CLOSED. No physical
FTP/deploy/test, driver/settings/UI/policy change, or reuse of168's failed case.

Two independent live IDT gates locate the actual matching kernel at0x82403000,
different from the static physical lead0x823d0000. The new observer derived
kernel sites after this identity check.49 events capture24 process creations,
24 returns paired by ETHREAD AND exact stdcall stack, then NtShutdownSystem.
Every recorded resident pin independently rechecked against cold binaries and
their actual relocation delta;2 nonresident hits retained, no pages forced.
No pending returns, every breakpoint removed, guest resumed. No hard-error hit
before the observed final kernel shutdown entry. Capture stopped there, so it
does not prove absence after that point or identify an unobserved error producer.

services.exe PID208 created:

- `rundll32.exe newdev.dll,DevInstall PCI\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\2&ebb567f&0&28`:
  creation flags12, inner returnTRUE, returned child PID944/TID732.
- `rundll32.exe newdev.dll,DevInstall PCI\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1\2&ebb567f&0&09`:
  flags12, inner returnTRUE, returned child PID732/TID944. Entry tick6505,
  return6506; final winlogon.exe PID180 shutdown tick6688/action1.

Inner creation success is not outer CreateProcessAsUser success or child startup
success. The recorded immediate caller is in a different user module from the
UMP preferred-address lead; no UMP caller pin was hit. Do not attribute that frame
or infer the old token-handle failure from these numeric handles/PIDs. Actual
parent commands and creation commands were read in the current parent's address
space; child PIDs came from returned PROCESS_INFORMATION.

Read-only before/after hive inventory identifies01B0 as “Multimedia Audio
Controller” and01B4 as “PCI Device”; neither has Driver/Service binding in either
preserved current control set. This establishes genuine pending installer work,
not the root cause of the earlier popup or a reason to suppress device discovery.

5 samples/20 copy checks/25 loops/50 RAM-versus-scanout RGB coherence checks PASS,
normal shutdown/dashboard. Full cold allocation322 directories/6721 files/323
directory clusters, zero errors/orphans;5 structural hives, all protected hashes,
startup exact.36 frozen inputs and source snapshots exact. No new application
events or system popup; sole inherited exact Ftdisk49 makes strict qualification
FALSE. Debugger scheduling changed: no ordinary/performance/physical promotion,
and absence of the popup does NOT settle167/168 failures.

Actual NT5 timing DDI signatures/import reviewed; runtime frequency/monotonicity
and engine-versus-upload latency remain pending. See TIMING-PLAN.md for the
bounded next113 diagnostic. Existing physical0101/video0093,0088 rollback and
immutable0.1.0 untouched. Never relaunch/recollect168 or169.
