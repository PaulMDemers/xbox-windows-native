# 554 Xbox sustained software scene: scoped PASS

One user-confirmed cold start, one ordinary launcher request and one automatic
Windows restart. Both default and HEL software D3D7 processes completed 2,560
frames in five 512-frame batches. All ten independent image endpoints pass,
including geometry, texture/depth order, native conversion, clipping, GDI
readback and unchanged sources. API success is checked on every submitted frame;
only the five endpoints per process are image-checked. The sample executable
is byte-identical to the qualified 553 PC sample.

The Xbox reports QPC frequency 1,125,000 Hz. Both 250 ms and 1,000 ms clock comparisons
pass the pre-existing tolerance (max 32 ms or 5%) against GetTickCount in both
processes. Default reports 255/1,005 ms versus 253.188/991.780 ms; HEL reports 255/1,005 ms
versus 241.538/991.471 ms. These are guest-clock cross-checks, not calibration
against an external time standard. Unlike PC 553, derived QPC phase durations
are retained here; the PC clock failure is neither repaired nor erased.

The table reports aggregate milliseconds for 512 frames per batch, rounded to
three decimals. Render includes target-lock completion; upload includes CPU
readback/conversion; present includes primary Blt/GdiFlush, not physical scanout.
There are no deliberate sleeps, report writes or capture-file writes inside
these phases. Counter overhead and unrelated scheduling can contribute.
Do not convert these small-scene API measurements into game FPS.

| Backend | Scene | Coarse batch ms | QPC batch ms | Render ms | CPU upload ms | Present API ms |
|---|---:|---:|---:|---:|---:|---:|
| default | 0 | 780 | 782.342 | 430.865 | 93.228 | 254.798 |
| default | 1 | 870 | 873.412 | 404.914 | 80.380 | 384.681 |
| default | 2 | 810 | 796.349 | 346.715 | 84.373 | 361.883 |
| default | 3 | 540 | 532.684 | 241.245 | 73.421 | 214.750 |
| default | 4 | 615 | 620.932 | 327.664 | 72.259 | 217.524 |
| hel | 0 | 645 | 656.891 | 354.893 | 81.445 | 216.897 |
| hel | 1 | 735 | 727.470 | 330.035 | 75.928 | 318.261 |
| hel | 2 | 720 | 715.580 | 321.069 | 75.386 | 315.901 |
| hel | 3 | 540 | 540.598 | 242.967 | 83.780 | 210.580 |
| hel | 4 | 615 | 620.914 | 329.045 | 76.380 | 212.220 |

Commit stays 667,648 bytes at every before/after batch snapshot in both processes.
After graphics release it falls 90,112 bytes to 577,536 bytes, still 360,448 bytes
above the pre-graphics snapshot. Windows/GDI/PSAPI still exist then; this is
neither a leak diagnosis nor long-run leak-freedom proof. Peak commit is 696,320
bytes and peak working set 2,068,480 bytes in both processes, below the frozen 8 MiB
bounds. Final COM-release and texture-preservation checks pass.

All 49 files have matching paired cold reads. Twelve live/cold modules per process
match, including PSAPI and all eleven pinned runtime DLLs. All five before/after
hives pass the independent checks, with the inherited typed SOFTWARE DRM
limitation; no complete FATX allocation/ownership audit was performed. EventLog
6006 increments once and the runner records two zero exits and a restart request.
New Ftdisk 49 remains; no new Application Popup was decoded in this sequence.
Consequently strict system qualification remains false, and prior shutdown-popup
limitations are not claimed fixed. 616 malformed actual-telemetry controls are
rejected. Existing 16 controller-model cases and 24/54 import checks remain pinned.

The owned hook was removed as the first remote mutation after dashboard return.
Protected 720p, ordinary launcher and ordinary startup remain exact. Console C
was not accessed. All owned supervisors/observer are closed; 57 frozen inputs are
archived privately. Console was last authenticated at the dashboard; no further
launch is queued. Never rerun, recollect or parent this closed attempt.

This qualifies the bounded software sample and checked windowed pixel endpoints.
It does not establish NV2A acceleration, game compatibility, boot reliability,
physical scanout quality, broad performance or clean-install release readiness.
Boot investigation remains tabled. 552 remains a failed timing attempt and 553
retains unqualified QPC-derived durations.
