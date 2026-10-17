# Physical RGB32 color-key diagnostic passed

The watched retry completed on the Xbox at the existing 1280×720×32 desktop.
Default and HEL each completed all 12 stages, exited0, and matched all source and
destination bytes: 92,160 bytes total, with zero mismatches. These stages cover
three full-width RGB32 keys, plain and keyed copies, and clipped and unclipped
copies. This is an offscreen system-memory result, not a scanout or GPU result.

The probe is exactly the 446 executable, SHA256
`0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c`.
That binary failed keyed comparisons on the PC 16-bit desktop and passed on the
PC 24-bit desktop. The new Xbox 32-bit result confirms this diagnostic works in
the installed Xbox configuration without changing the sample, DLLs or driver.
It does not identify the faulty instruction/component in the 16-bit PC path or
qualify the later full rung 04 sprite/overlap stages.

## Attempt and cleanup

The user requested another attempt while watching after 448 produced no receipt.
The 449 controller and eight supporting source files differ from 448 only in their
namespace/schema. Reversing the substitutions reconstructs the original bytes.
The controller was built under the shared build lease with the pinned compiler,
no warnings, and 24 actual NT5 import matches; the unchanged probe has 23 matches.
Controller SHA256 is
`d4a9b0cdd92705e284bb61441925ce3c4a228ff6fb79eca93ce6e9e3047bdde4`, 12,958 bytes.
No previous result namespace or startup hook was reused.

One SITE EXEC request was accepted at 19:48:16 UTC on October 17, 2026. The bounded
observer found the new runner receipt at 19:49:40 UTC and closed normally without
a deadline. Both 90-second process waits completed normally. The controller
recorded restart privilege/request success; the user reported a clean boot to
the desktop and restart. A new EventLog 6006 independently supports normal shutdown.
Collection completed at 19:49:55 UTC after removing the temporary startup entry
and preserving it under E:/xwn449-kit/startup-used.cmd. The normal startup file,
launcher, protected code and 720p baseline verified unchanged. Dashboard C was
not accessed. All owned host processes are closed; never rerun or recollect 449.

## Independent checks and limits

The independent checker accepted both reports, external process exit receipts,
and all raw source/destination captures. Changes to every reported scalar, every
destination pixel, sampled source bytes and capture lengths produced 19,592
rejections. Original captures remained unchanged. All five registry hives passed
clean header and independent raw-value checks. Twenty-seven private before/after
files and 21 frozen dependencies were rehashed. Private Windows files and raw
captures are not included in the public repository.

Strict system qualification remains FALSE. This boot recorded Ftdisk 49 and one
Application Popup 26: rundll32.exe failed initialization because the window station
was shutting down. No event was suppressed or waived. Event-record scanning does
not prove active-ring completeness, and no full FATX allocation audit was done.
There is no new performance, D3D, native GPU, game or physical scanout claim.
The preceding 448 no-receipt attempt and the user's qualified recollection are
preserved separately; a successful retry does not resolve its cause.

See final-review.json, runtime-review001.json, actual-controls001.json,
source-review001.json and the physical001 lifecycle receipts for exact evidence.
