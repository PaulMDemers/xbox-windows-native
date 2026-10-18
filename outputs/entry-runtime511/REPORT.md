# Entry runtime 511: closed observer refusal

One fresh emulator run of exact510 was launched at 10:00:39 UTC and stopped at
0x11100. The five bytes E9 FA 39 08 00 matched the pinned candidate. The observer
refused before executing that jump: it incorrectly required the loaded header's
entry field to retain the encoded on-disk value. Actual loaded entry was 0x11100;
on disk it is 0xa8fd46ab. This is a harness failure, not an Xbox boot result.
No diagnostic API call, receipt, firmware return, or Windows execution occurred.

Host001 had passed113 invalid-state/stub cases and four transport failure points;
12 actual cleanup paths and host002 seven cleanup failures were exercised with
modeled CPU/transport. Their loaded-header fixture incorrectly used disk bytes.
All original source/results remain immutable. The planned success-only reviews
were not executed. failure-review001.py records the actual refused outcome.

Breakpoints were removed, physical mode restored, and the owned host exited0
without fallback. All342 private files,259 frozen repository dependencies and17
external inputs were rehashed. Sessions76640/50684/35492 are CLOSED. No physical
access, startup hook, or queued launch. Initial read of nonexistent507/trace.py
failed harmlessly; trace001.py was then read.

Cold audit covers the complete10GB mapping and reports55 changed bytes, so strict
whole-disk equality remains FALSE. Writers are not fully attributed. FATX has
276 directories,6553 files,255 directory clusters, zero errors/orphans. All five
hives and three protected baseline binaries are byte-identical; source and EEPROM
are unchanged. No receipt exists. These facts do not turn the failed observer
into a successful jump or ordinary boot.

See final-review.json, emu001/trace.json, audit.json and protected.json. Do not
relaunch, recollect, or parent this closed runtime.
