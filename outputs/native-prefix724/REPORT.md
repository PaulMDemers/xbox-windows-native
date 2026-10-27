#724 CLOSED: native prefix passed forward checks; cleanup failed

One accepted launch2026-10-27T17:26:43.374871+00:00. User observed orange held
picture and provided private photo. Top bar green. Photo decoded independently
with components, five sample positions, three brightness/color-floor thresholds,
and adjacent-row interpolation. User subsequently power-cycled; nine fresh
preparation files collected ONCE/double-read. audit001 passed; stage/source/build
pins and unrelated E directory entries unchanged. Console now at UnleashX.
No startup hook, Windows run, owned host process or VM. No new test staged.

## Physical optical result

| Row | Meaning | Value |
| --- | --- | --- |
|0|Signature|7240000d|
|1|Bridge phase|4|
|2|Admission stage|5|
|3|Return code|7245 (cleanup failure)|
|4|MMIO attempts|11|
|5|CRTC attempts|4|
|6|First forward mismatch|ffffffff (none)|
|7|First actual|ffffffff (not applicable)|
|8|First expected|ffffffff (not applicable)|
|9|Cleanup OK|0|
|10|CR19 cleanup|51|
|11|CR1b cleanup|85|
|12|CR22 after|fe|

All11MMIO and fourCRTC writes passed immediate readback, includingCR1b05.
The later cleanup sample readCR1b85, which violates this probe's05 expectation.
CR19 was51 andCR22 remainedfe. The code stops before anyCR22 data write.
This differs from closed kernel723, whereCR1b stayed05 through cleanup.
The photo does not export all other cleanup fields; additional mismatches remain
unknown. It does not establish why/when bit7 returned or define bit7 semantics.
No mask relaxation, repeated write,85 restore, timing replay or driver fix.

## Context and limits

Kernel prep last phase handoff_armed. PCI/CRTC/sequencer/geometry/allocation-plan
values exactly match closed720 preparation. File pre-arm CPU is
EFLAGS286,CR08001003b,CR3f000,CR4610; it precedes final handoff and cannot
substitute for native CPU data. CPU models remain separate from physical evidence.
The actual native payload returns to its owned bridge and deliberately holds;
manual power cycle is not a normal Windows shutdown or successful kernel return.

This isolates a native cleanup/readback difference after a successful forward
prefix. It does not yet locate the full-mode708/709 black-screen failure or
qualify native1.6 mode switching, Windows, or GPU acceleration.

Preserve build001 undefinedVIDEO_MODE_724P, build002 parser failure, and the
photo001 decoder rejection (green cast reduced one white sample's blue channel
to172). Corrected build003 and photo002 passed their documented checks. Private
photo is hashed; no photo, executable, firmware or credentials are published.
