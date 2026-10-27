# 736 CLOSED: first post-write CR1b read85 after CPU-only work

One accepted launch2026-10-27T20:47:21.191068+00:00, preparation6a586a24.
The4093 register-only iterations completed before the first direct read; all16
direct and16 reselected reads were85. Work counter0/checksum793a7efe was
independently recomputed.630 snapshots remained2. Fields2..79 exactly match735.
Deferred full-byte check still rejects expected05 versus85 at check15/index14.
Full cleanup mask0, selectors and flags restored. Actual critical CPU
8001003b/f000/610; entry/critical/restored flags246/46/246.

This removes a preceding post-write read as a necessary condition for obtaining85
after the work. Together with735 it removes a specific eight-read requirement.
It does not establish a calibrated delay, bit7 meaning, or full-mode safety.
No mask, repair write, CR22/CR33 data write, or functional driver patch.

Screen unobserved under explicit unattended authorization. Timeout and connection
refused observations retained; dashboard reachable20:48:03UTC. Seven reports
collected once with double-read identity; audit001/analysis001 PASS. Automatic
return inferred from restart_requested plus dashboard reachability; not a
Windows normal-shutdown result. No hook or owned process/VM. Console dashboard.
All736/prior runtimes CLOSED. Protected720p and ordinary launchers unchanged.
