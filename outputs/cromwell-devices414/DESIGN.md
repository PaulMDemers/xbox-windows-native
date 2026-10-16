# 414: original USB and IDE initialization up to loader dispatch

No guest build or physical deployment. One fresh child of never-executed412
preparation002, same original374 launcher and same emulator USB keyboard/mouse
configuration as413. Original entry and relocated full payload remain pinned.
New stops cover USB call/return, IDE call/return and BootFromDevice call BEFORE
execution. This is a bounded debug trace, not an ordinary boot or physical test.

Capture actual60-byte vmode, framebuffer register and bounded physical memory
before USB and before loader dispatch. Require exact supported1280x720x32 layout,
software framebuffer base and register agreement before any framebuffer read.
The pinned original framebuffer helper uses width*4 pitch. Render these owned
memory bytes as observational images, not an independent pixel correctness or
actual TV scanout oracle. Unsupported geometry/range fails; no fallback guess.
Do not issue the unsupported screendump command from failed413.

Per-stop35seconds and total240-second host watchdog. One SITE request, no repeat
on timeout. Preserve partial state; remove hardware breakpoints, restore physical
mode and orderly stop/quit. No guest memory/register edits. USB/IDE call-return
does not prove all attached devices work; never infer physical Razer behavior
from the generic emulated keyboard. BootFromDevice and Windows remain unexecuted.

Full cold mapping/allocation/EEPROM/seed audits and complete E file hashes,
including original failed disk-equality gate. Preserve consumed413 unchanged.
