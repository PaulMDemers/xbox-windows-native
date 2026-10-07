# Aligned first installation with coordinated GDI load

Owned emulator diagnostics only. Both cases are fresh siblings of the immutable
padded pre-install fixture from fatx-install-alignment/fixture-001.json. The same
new helper replaces only xwnidle/probe.exe; one mode byte is0(control) or1(load).
Padded SetupAPI log, startup, all five hives, INF, FATX0101 and video0093 remain
unchanged at staging. New helper and mode file are readback/hash verified.

Original matcher/action functions and globals before the entrypoint are preserved
with only line-ending normalization for comparison (ui-preservation.json). Exact
successful GPU Finish, same-process restart No, and command-line-identified xemu
placeholder Cancel remain bounded once-only actions. Unknown dialogs are untouched.
Queue-idle and completed-action gates remain, plus drawing worker stop/join gates.

Both modes create the same owned window and GDI resources. Mode 1 draws 512x320
colored bands via FillRect/BitBlt/GdiFlush every 10ms. Ready is signaled only after
its first successful drawing cycle and a read-only SetupAPI size observation.
Mode 0 creates resources but performs no loop drawing. Neither mode has direct
GPU/register access or changes driver binaries. The worker adds one log-size read
at readiness; the main thread samples size/activity five times at 0/30/60/90/120s.
This read-only observation still perturbs timing and is explicitly diagnostic.

For mode 1 coverage, first completed drawing must precede appearance of the target
warning bytes (observed EOF<=270225), the final size must exceed the full warning,
activity must continue between samples, and cold alignment must still be exact.
This brackets file growth while the worker runs; it does NOT establish overlap
of individual kernel I/O/drawing calls or observe the SetupAPI source buffer.
If readiness is late, preserve a missed-coverage result. Do not call it a pass.
Mode 0's coverage gate is inapplicable and true by convention; its counters must be 0.
The same installation/file/event/hive/allocation gates apply to both modes.

Run Build.ps1 then review.py probe using the pinned owned compiler/DLLs. Prepare
one fresh case using prepare.py, audit-before.py, then the unique Run.ps1 and
local supervise.py. After dashboard return and cleanup, collect once, qualify,
then compare only completed evidence. No relaunch of recorded attempts. Raw
images/hives/logs remain private and ignored. No physical console endpoint is
used. No ordinary stability, acceleration, performance or release claim follows.
