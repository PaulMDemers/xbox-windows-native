# PC570 CLOSED: foreground gate rejected before game input

The game rendered its title menu but did not acquire foreground during the
60-second readiness bound. No game test click, key press or native capture
occurred; only the four unconditional cleanup input-release events were sent.
The title signature matcher therefore remains untested at runtime. Empty
capture results are explicitly unqualified, not a vacuous pass.

Periodic window records show client36,55,640,480 on an800x600 desktop, with
focus0. The initial invalid state line's zero geometry came from short-circuit
evaluation before the geometry calls; it is not a measurement of zero size.
Future state reporting must collect readable context before deciding validity.

Game exit0, no forced termination, exact registry restoration, five clean hives
and one new6006 normal-shutdown event passed. VM exited0 at08:00:56UTC without
host quit/deadline. Source404 and helperISO remained exact. All owned processes
are closed. No Xbox access, hook, game-performance or acceleration result.
The first Display Properties confirmation expired and reverted the mode; the
second was confirmed at800x600. Start balloon dismissal was host shell setup
during copying, before the game started; all inputs/screens are retained.

The source minimized its console before creating the game. SW_MINIMIZE also
activates another top-level window according to [Microsoft's ShowWindow
reference](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow).
This is a plausible harness cause, not a proven game or driver defect. A fresh
control should preserve launch foreground and make one recorded request for
the owned game, then verify actual foreground. A successful request is not
guaranteed by satisfying the listed conditions; see [SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).
Never change foreground-lock policy or attach unrelated input queues to force it.

Next retain title/exposed-target checks, report foreground PID/class even on
rejection, and close normally immediately after completion or failure. Do not
idle to the old300-second observation bound. Never rerun/recollect/parent570.
