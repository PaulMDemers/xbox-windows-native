# Kernel mode comparison722

One accepted launch at2026-10-27T16:40:07.389661+00:00. User saw all three
12-second stages as expected: blue1280x720, green720x480, cyan1280x720, then
an automatic return to UnleashX. No manual reset. These are SDK/kernel-created
32-bit60Hz progressive modes; no Windows or native video initialization.

Eleven flushed/readback report files were collected once, read twice identically,
and audited against staged executable/source pins. Allocation extent, every
framebuffer page, stride, scanout, format, dimensions, flags and index restoration
checks passed. Six captures (before/after the visible hold in each mode) have
identical sampled MMIO/CRTC values within each stage. This is sequential capture,
not an atomic hardware snapshot or proof of no transient changes.

CR1b=85 and CR22=fe in all six captures. Register680630 is3/2/3 across modes;
680880 remains21101100. All11 common PRAMDAC setup words equal704's values in
working720x480. Eight of14 timing values and14 of22 masked CRTC geometry checks
match. The three common CRTC differences are19 (3a versus final30),1b (85 versus05)
and22 (fe versusff). See comparison001.json for exact values and masks.

| Timing offset | Native704 target | Working kernel720x480 |
| --- | --- | --- |
| 68080c | 489 | 488 |
| 680810 | 492 | 493 |
| 680824 | 779 | 857 |
| 680828 | 719 | 679 |
| 68082c | 738 | 761 |
| 680830 | 770 | 767 |

Different working register values do not identify the first failure in708/709,
prove the native recipe invalid, or authorize replaying the kernel's state.
704 expects05 atCR1b during setup;721's failed85 restoration is not itself proof
of that setup failing. CR22 semantics remain unknown. Capturing fe in a working
mode does not prove what a write offf would read back.

Validation: fresh nxdk build001;771 actual-COFF modeled capture cases including
index restoration faults;3445 actual-COFF layout/pixel cases. Capture writes only
48 index-selector bytes, never GPU data registers; the supported kernel mode API
performs normal mode programming. All nonrelocation capture/layout instruction
bytes match both linked PE and XBE. Maximum modeled capture critical path1823
instructions, not a hardware time bound. Kernel mode/file calls can still hang.

No new build/test failure; initial offline-comparison patch formatting was
rejected before application and corrected. No physical impact. All earlier
failed/closed attempts preserved. Selected E entries/files verified; no claim
of complete FATX/hive audit. Dashboard return is firmware restart, not Windows
normal shutdown. Console at dashboard; no hook/process/VM. See NEXT.md.
