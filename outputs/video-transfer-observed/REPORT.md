# Installed software transfer route captured

trace003 is CLOSED and diagnostic PASS:138 events,63 paired calls,240 resident
code pins, four complete small/large upload/overlap brackets, no pending calls,
all breakpoints removed and guest resumed. The helper completed54 cases and162
full RGB stages and restarted normally. Full cold allocation324dirs6755files/
325clusters, five hives/protected binaries, unchanged pagefile/configuration and
zero warning/error/application deltas all pass. This debugger run is not an
ordinary performance qualification. See trace-verification.json for checks.

All four selected public BitBlt calls enter the actual service-table target for
the pinned NT5 GDI syscall100d, reach EngCopyBits and return success. The following
GdiFlush calls enter service1093 and return independently; no Eng drawing export
was observed inside those flush brackets. This is execution evidence, not proof
that a flush costs zero time or a substitute for general GPU synchronization.

The actual desktop SURFOBJ is a1024x57632-bit engine bitmap, stride4096. Upload
sources have the expected padded DIB dimensions/strides. EngCopyBits' observed
indirect dispatch at win32k RVA26e60 targets RVA117125 in all24 captured such
calls. Static inspection of that pinned target shows a row loop with two possible
copy callees; the choice between those branches was not captured. No symbolic
name is assigned to the private routine merely by resemblance.

|Selected operation|EngCopyBits calls|Observed indirect row-copy calls|
|---|---:|---:|
|64x64 upload|1|1|
|64x64 overlap|1|1|
|768x384 upload|4|7|
|768x384 overlap|15|15|

Large cases include31x27 surfaces with negative124-byte strides and transfers
around screen rectangle500,276..531,303. The expanded route is consistent with
software pointer save/restore and clipping. That inference motivates the new
matched visible-arrow inside/outside experiment; the trace itself does not
attribute elapsed time to cursor handling. No hardware speed claim or driver fix.

trace002 is a separate CLOSED host preparation failure: probe.c was omitted
from the copy filter. No fixture/seed or guest existed. Its failed preparation
source and record remain. The original trace001 E14 failure also remains intact.
trace003 used the exact same compiled probe with improved observer diagnostics;
all drivers, mode and inherited emulator-only device policy stayed unchanged.
