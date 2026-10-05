# Physical GDI baseline003: PASS

Launched once at2026-10-05 21:25:15 UTC. Dashboard return observed at21:26:47 UTC.
All four pixel checks and five timing loops completed. The runner requested a
normal restart and the new system EventLog6006 confirms normal event-log shutdown.
Collection restored original startup before retrieving logs. All six baseline
binary hashes and both helper hashes match. No new application events, delayed-
write popup, or unexpected warning/error was recorded. Recurring Ftdisk49 is
identical to pre-run evidence; this is not a claim of an entirely clean event log.

The unchanged physical mode reports1024x576,32bpp,60Hz. The reported60Hz is a
miniport value, not an independent measurement of encoder/field timing.

| Operation (256x128 pixels) | ms/operation | MPixels/s |
| --- | ---: | ---: |
| opaque fill | 2.10 | 15.62 |
| DIB to screen | 2.36 | 13.87 |
| screen to DIB | 50.14 | 0.65 |
| overlap right/down | 56.67 | 0.58 |
| overlap left/up | 29.71 | 1.10 |

Each operation includes GdiFlush, message processing and visibility checks.
This is one bounded sample, not window-drag FPS, pure memory bandwidth, variance
across boots, or general storage qualification. Screen readback and overlapping
copies are markedly slower than fills/uploads here. Investigate that path;
these timings alone do not establish whether cache attributes, copy routines,
or another mechanism is responsible. No performance candidate was deployed.

## Corrected trace lifecycle

Attempt002 stopped before the probe because the new harness omitted the existing
one-shot trace reseed. Its photo and4096-byte readback match the known logger
guard at offset16, with41 prior records. Attempt003 preserves that trace, checks
its marker/size, writes the exact clean seed, verifies readback, and rechecks it
before launch. Unknown identity/size or a bad readback blocks launch. Four offline
regression tests cover populated/empty seeds, wrong identity/size and corrupted
readback. The runner's NT5 imports were checked after rebuilding its private paths.

The driver, HAL, loader, mode and GDI probe were unchanged. Trial003 retained the
post-run trace before any next-boot preparation. `prepare-next-boot.py` only resets
that diagnostic file after verifying ownership, unchanged binaries/startup and
its exact collected contents; it never launches Windows. `next-boot.json` records
whether preparation completed. This is only one-boot readiness. Removing the
one-shot trace dependency is still required for repeated manual-menu launches.

`trial.json`, `observation.json`, `qualification.json`, and decoded event logs
are the reproducible evidence. Private binaries/raw EVT/trace files remain under
ignored artifacts. Attempts001/002 remain preserved failures/unexercised tests;
this PASS does not reclassify them. No observer or emulator remains running.
