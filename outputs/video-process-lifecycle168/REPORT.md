# Preserved failed trace; workload and cold integrity passed

ONE launch accepted 2026-10-08 23:35:18 UTC, dashboard returned23:37:34.
The observer failed its static expected-kernel-base assertion at the first hit,
before recording any creation event. Two IDT gates and matching kernel metadata
were discovered, but the failed source did not save their values before asserting.
The actual base is therefore unknown in this attempt's preserved JSON. Do not
infer it from a physical address or silently edit the frozen source.

All three breakpoints removed, guest resumed, observer89741 CLOSED. Runner30178,
supervisor17282 and cold audit90653 CLOSED; no relaunch or repeat collection.
`candidate001/trace-verification.json` records diagnostic capture incomplete.

Existing167 v4 probe/166 launcher completed5 samples,20 copy checks,25 loops,
50 RAM/scanout RGB coherence checks and normal restart/dashboard. Cold full
allocation322 directories/6721 files/323 directory clusters, zero errors/orphans;
5 structural hives, all protected hashes and startup exact.36 frozen source pins
and source snapshots exact. No driver/settings/device/UI change or physical access.

Strict result remains FALSE: exact inherited Ftdisk49 plus TWO informational
Application Popup26 entries naming rundll32 DLL initialization failure because
the window station is shutting down. Application-log delta empty. The popup
recurred, but its parent/command was not captured; this run cannot identify cause
or qualify ordinary performance. Timing samples are descriptive debugger data.

Fresh successor169 derives kernel sites from the live verified image rather than
arming physical absolute-address leads. This is a host observer correction,
not a guest driver patch. Never relaunch/recollect168.

Owned NT5 Win32k/DDK inspection also verified VOID pointer-output timing APIs:
EngQueryPerformanceCounter and EngQueryPerformanceFrequency both call the actual
KeQueryPerformanceCounter import. Static interface checked; runtime timer contract
and rendering/upload latency split are still pending. No optimization justified yet.
