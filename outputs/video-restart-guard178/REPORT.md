# Ordinary launcher refuses restart with device installation pending

The new owned launcher recorded `INSTALL_WAIT_RESULT 258` followed by
`RESTART_BLOCKED_PENDING_INSTALL 258` after all five graphics samples. It never
recorded a normal restart request. This validates the guard's refusal path in an
ordinary emulator execution. It is a held test, not a successful reboot, soak or
fix of the separate shutdown popup.

Single launch accepted2026-10-09 01:49:42.740419UTC. Owned runner21685 and
supervisor52283 CLOSED; host210second bound closed the emulator at01:52:42.5044345
UTC, preserving the private disk. Audit50211 CLOSED, all sources frozen before
bootstrap. No debugger, UI action, physical FTP/deployment/test, Windows binary,
driver, setting or device policy change. Only the owned path-derived runner changed.

## Genuine guard behavior

The runner calls actual CMP_WaitNoPendingInstallEvents with a30000ms bound after
its existing workload/30s interval and privilege preparation. If idle, it checks
again with zero timeout immediately before ExitWindowsEx. Pending, failed or
unexpected results log the raw status and exit without requesting restart.

The same header compiled into the guest was tested under GCC ASan/UBSan: eight
cases covering idle, pending first, stale idle then pending, query failures and
unexpected results at both queries, plus restart API failure. Requests remain
zero on every non-idle branch. Actual RosBE2.2.1 NT5 imports and dynamic SetupAPI
export were checked, and all provider bytes including SetupAPI were cold-matched
to the actual parent during preparation/preflight. `build-review.json` retains
source/header/compiler/executable/provider pins. An initial unavailable-clang
host refusal is preserved; no executable or guest resulted from that attempt.

In this run the first query returned WAIT_TIMEOUT258, so no second query or
restart request was recorded. The compiled blocked branch closes the log and
exits13; actual ExitProcess completion was not separately observed and is not
claimed from the log alone. `guard-verification.json` checks exact records,
frozen40pins/source snapshots, builds, cold results and lifecycle predicates.

## Desktop and device state

At01:51:58UTC a brief read-only monitor pause/capture/resume showed the desktop,
Getting Started window and two Found New Hardware wizard taskbar entries.
No controls were clicked. Device text was partly covered, so the screenshot does
not identify either wizard's device. PNG retained privately with hashes/metadata;
explicit1024x576/pitch4096 matches prior runtime caps but is not independent mode
discovery. No performance qualification follows from this observational pause.

Separate before/after cold hive inventory shows01B0 “Multimedia Audio Controller”
and01B4 “PCI Device” each still lacks Driver/Service bindings in ControlSet001.
The query establishes pending installation, the screenshot establishes visible
wizards and hives establish binding state; these are distinct evidence sources.
No unsupported device was silently marked installed or suppressed.

## Cold results and qualification

Five sample exits0,20pixel-copy checks,25timed loops and50full-scan RGB coherence
checks PASS. Full allocation322directories6721files323directory clusters,zero
errors/orphans;5structural hives and35protected file hashes/startup bytes PASS.
The bounded host stop is intentional and not a normal guest shutdown. There was
no EventLog6006 or dashboard return. Full lifecycle workload and strict
qualification remain FALSE. Sole warning/error is the unchanged exactFtdisk49;
no application-event delta or popup. Popup absence without shutdown is not a fix
or comparable to a completed reboot. Original physical0101/video0093,0088rollback
and immutable0.1.0 remain unchanged.

Frozen emulator-ready.scope accidentally retains inherited ownership-observer
wording. Preserve it rather than rewrite evidence; actual Run.ps1/launch/audit
flags, changed runner and DESIGN distinguish this ordinary guard from177's
debugger run. It grants no ordinary/physical/performance qualification.

Next: complete genuine supported-device installation or obtain an explicit
unsupported-device outcome, then run a fresh guarded ordinary reboot. Two idle
queries cannot atomically exclude future queued work; the guard does not patch
Windows' token ownership race. Retain held178 and all previous failed evidence,
strict event gates, physical baseline and recovery bundles. Graphics optimization
can proceed in a properly settled fixture after setup is resolved; no speculative
UMP/driver fix or automatic unidentified wizard actions are justified here.
