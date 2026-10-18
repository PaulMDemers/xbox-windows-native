# 541: later checkpoint prepared and staged; not launched

The source/binary review locates the next boundary at02600200, immediately before
the jump into BootResetAction at02600420. The preceding unchanged interval clears
100876 bytes of BSS and20480 bytes of IDT RAM, loads IDTR, initializes the FPU,
and performs the original cache/control/MTRR setup. The original final CR3 write
uses operand0800; this is recorded exactly and is not treated as a diagnosed bug.

The new marker is green/amber rather than red/green, reducing ambiguity with the
prior observation. The former post-stack detour is removed, the marker is placed
at the later boundary, and it deliberately holds before C/Windows. Removing the
earlier marker also removes its earlier I/O/delay;541 cannot isolate those effects
or retrospectively explain539. No functional boot/driver/reset change is proposed.

Original374 source files, map, ELF and binary are hash checked. Public
BootResetAction.c matches the pinned build source exactly. Review identifies
memory/interrupt/PCI/AGP/cache/CPU/EEPROM setup before its video initialization.
The first-C function has not executed in this new test because no launch was sent.

Six host setup cases pass: two images, two DF-clear flag combinations and a
DF-set negative case for each image. Actual memory-writing/arithmetic bytes are
executed; privileged register/cache effects are explicitly modeled. Forty actual
marker/caller cases pass with modeled SMBus/TSC, plus19 controller and6 stage/
capture cases with modeled FTP. These do not qualify physical cache or devices.

Package001 freezes55 input pins. Candidate542839 bytes has SHA256
fbcdd7cfae25181bb2165755771bb20064d61a2c5ec0774d6fb9c2a4b0840876.
It reconstructs the original490 build exactly after undoing the declared patches,
same-length namespace substitutions and section digest. Payload length and all
other loader bytes are unchanged. Private build: C:/xwn541/package001/default.xbe.

Stage completed21:42:40UTC under unique owned E:/Applications/XWNBoot541a with
exact readback. Only that directory, owner.json and default.xbe were written.
Protected720p and ordinary startup/launcher checks passed before and after.
No hook or Xbox C access; host stage process closed, no launch queued or sent.

Watcher/reset readiness is pending in the user question. The test intentionally
holds on black after a bounded LED transaction; it is not an automatic-return
test. Await readiness before the one allowed launch. See DESIGN.md and NEXT.md.
All previous runtimes remain closed; the automation remains paused.
