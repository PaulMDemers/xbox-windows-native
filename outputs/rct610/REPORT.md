# PC610: original DLL unload, reload and address reuse passed

The original A/B/A control loaded three module generations at 0x62000000 and
reused the same return address. Each generation made a traced GetProcAddress
call, returned its expected value, verified its restored instruction byte and
unloaded. The recorder read fresh bytes 0x90, 0xf8, 0x90, retired each completed
return site and never reused a historical site's byte. Pristine and traced
subject logs matched exactly. This qualifies the narrow lifetime handling that
PC609 lacked; it is not a new game result.

The shared admission routine rejects pending calls, single-step or held-thread
state, active entry sites, enabled/armed/referenced return sites and inconsistent
ownership before any retirement. Active module ranges cannot overlap. Unload
does not read or write the departing image. Old breakpoint records remain
historical and cannot match new exceptions. The conservative guards remain.

Host sanitizer checks passed the retained call, DIB and phase controls plus
19 read-only lifetime rejection checks. The actual cold trace passed the
retained 23 structural, 11 phase and 7 absent-output mutations, plus 16 new
lifetime mutations. The new cases reject missing retirement/ownership/code
records, reused generations and an old image's instruction byte.

The fresh immutable404 child exited at 2026-10-20 16:01:10 UTC after the
runner requested normal Windows restart. Cold enumeration covered 6,494 files
and 310 directories; all tools and protected OS binaries, the immutable seed,
five clean hives with raw-value agreement and one new EventLog6006 passed.
Raw timestamps put shutdown after startup even though record ordering differs.
All owned processes exited. No capture error or forced host reset occurred.

See review001.json, lifetime-oracle-tests001.json, host-tests001.json and
final001.json. Historical helper names and a few inherited console messages
retain older attempt numbers; receipts, paths and frozen hashes identify610.
The trace summary's breakpoint_sites counts currently active address records;
TOTAL includes historical retired records as independently checked by parse.

The Xbox, launcher, protected720p and packaged builds are unchanged. No hardware
reset, game/driver change, timing, FPS or acceleration claim follows from this
original PC control.
