# Reviewed xemu optimization: isolated Windows latency comparison PASS

The improvement code is already implemented in unchanged reviewed xemu build003.
This fresh ordinary timing pair uses identical RAM0112,compiled141 and immutable
parent children. ONLY the reviewed emulator binaries differ. Both fixtures,cold
configuration/pagefile checks and source preflights completed before either runtime.
Actual build/exclusive-xemu locks were checked before launch and after return.
No host build/preparation/cold audit,screen/state capture or debugger ran during
either measured workload; audits started only after BOTH guests and leases closed.

For the192x96 bottom solid rectangle, median primary draw latency fell from
4.38735ms to0.09820ms:44.678x control/candidate. Equal-area top and top-offset
rectangles stayed near0.10ms. Their predicted initial depth-watch intersections
are0/0/17280 pixels. Fragmented-horizontal and width-sweep rows crossing retained
watch addresses also improve sharply; memory-only timings remain close. The
separate lifecycle reconstruction proves the prelaunch linearZ16 watch is downloaded
and CPU-write-evicted only by candidate. It does NOT pair each GDI operation/store
with a specific watch or prove every slowdown is solely that initial depth surface.

## Primary draw latency (microseconds per draw)

Three rotated repetitions per geometry; medians with minimum/maximum. Sparse
firmware lifecycle trace and the same bounded loopback FTP observer remain enabled.

| Cell/layout | Control median [min,max] | Candidate median [min,max] | Control/candidate | Memory medians control→candidate |
| --- | ---: | ---: | ---: | ---: |
| 0: 192x96, kind0, (0,0) | 96.36 [95.39,150.30] | 98.24 [98.16,130.89] | 0.981x | 43.30→40.91 |
| 1: 192x96, kind0, (128,0) | 97.72 [97.43,139.96] | 96.88 [90.22,115.59] | 1.009x | 45.55→43.77 |
| 2: 192x96, kind0, (0,160) | 4387.35 [4358.81,9124.65] | 98.20 [94.71,117.70] | 44.678x | 39.99→39.79 |
| 3: 192x96, kind3, (0,0) | 1913.67 [1153.62,2104.85] | 107.06 [105.49,108.02] | 17.874x | 45.37→44.78 |
| 4: 192x96, kind3, (128,0) | 2039.23 [1249.85,2166.17] | 104.32 [103.92,108.73] | 19.548x | 45.45→43.77 |
| 5: 192x96, kind3, (0,160) | 4072.58 [3875.66,4474.11] | 103.26 [101.39,113.74] | 39.439x | 46.31→44.56 |
| 6: 192x96, kind4, (0,0) | 269.10 [265.18,275.65] | 267.60 [264.21,272.68] | 1.006x | 134.48→132.23 |
| 7: 192x96, kind4, (128,0) | 261.70 [260.08,265.32] | 267.57 [248.07,274.40] | 0.978x | 135.25→136.10 |
| 8: 192x96, kind4, (0,160) | 5038.65 [4946.08,6177.78] | 264.17 [263.86,285.23] | 19.074x | 134.85→138.94 |
| 9: 64x96, kind0, (320,64) | 629.22 [358.12,666.51] | 46.03 [45.32,48.88] | 13.670x | 20.37→20.21 |
| 10: 128x96, kind0, (320,64) | 1537.43 [1082.16,1904.07] | 70.48 [70.17,72.47] | 21.815x | 29.75→29.58 |
| 11: 192x96, kind0, (320,64) | 2773.17 [1809.04,2836.14] | 97.52 [96.91,102.85] | 28.436x | 39.41→40.59 |
| 12: 256x96, kind0, (320,64) | 3518.45 [3424.65,3968.41] | 121.02 [118.77,122.76] | 29.073x | 49.98→50.13 |
| 13: 320x96, kind0, (320,64) | 4452.61 [4321.49,4954.55] | 146.42 [145.67,148.30] | 30.410x | 59.16→60.61 |
| 14: 384x96, kind0, (320,64) | 5774.10 [5450.94,5952.08] | 171.86 [171.53,174.75] | 33.598x | 68.85→70.42 |

Kinds0/3/4 are solid,horizontal16,vertical16. Equal upload area is preserved;
fragmentation changes rectangle/row-copy cost. Full three-sample QPC ticks/loops,
coarse ticks,warmup/calibration counts and all30 path/geometry summaries are in
timing-comparison.json. QPC frequency1125000 is unchanged at each run end;
monotonic clock reads,sleep/coarse-clock cross-checks,all90 timing intervals and
quiet-counter/actual callback-byte relationships pass in BOTH runs. Independent
total BitBlt calibration yields65024 control/296960 candidate; those totals are
NOT a speed ratio.

Both ordinary strict cold audits PASS:45 functional cases,13,271,040 compared
pixels/run,45 exact independent reference files and45 RGB readbacks,normal
shutdown1/dashboard return,full clean327dirs/6851files/328dirclusters allocation,
zero errors/orphans,5 structural hives,protected/startup/payload/config hashes,
unchanged96MiB/1536-cluster pagefile and no warning/error/application events.
RGB channels0..2 are checked; alpha and independent physical scanout are outside
this protocol. Only BitBlt is exercised by this microbenchmark; other drawing
callbacks have separate earlier tests and are not newly qualified here.

Host checks:754 geometry,8 protocol,36 pixel,7 lifetime,24 timing/isolation
rejection cases PASS. All36 frozen input hashes and case source snapshots remain
exact; borrowed emulator sources remain restored. No relaunch/recollection or
failed gates were waived. Original Windows155 timing exclusion remains unchanged.

## Sampling and scope

This is one control-first pair with three rotated repetitions,cooperative host
resource isolation rather than exclusive OS scheduling. Small differences near
1x should not be ranked as performance wins; whole-boot time is not a speed metric.
The large affected-layout difference is an emulator microbenchmark improvement.
It is NOT physical video speed,interactive desktop FPS,new video-mode support,
or a comparison of RAM0110 against RAM0112. The guest optimization independently
proved4.71% fewer movement bytes and17.50% fewer repaint bytes with exact pixels
in video-window-foreground; a hardware latency gain remains unmeasured.

## Closure and next concrete step

All owned sessions CLOSED. Preparations73970/32755; control runner6648/supervisor
61626; candidate runner63186/supervisor12166; cold stages58914/63155; Windows
control verifier80410 and candidate/pair/timing/closer88005. Test runner32883 closed.
Inspect records; never rerun an attempt or completed cold stage.
control001: accepted2026-10-08T19:59:47.087444+00:00, returned2026-10-08T20:04:32.303860+00:00, lease closed2026-10-08T20:04:33.3765754Z.
candidate001: accepted2026-10-08T20:05:19.844518+00:00, returned2026-10-08T20:09:43.563939+00:00, lease closed2026-10-08T20:09:44.6236367Z.

Offline display bundle158 contains exact shared-UC provider/miniport/RAM0112
candidate files plus a separately readback-verified display rollback. Attempt157
refused the older0.1.0 miniport; failure remains preserved. Bundle158 is NOT
deployment-ready: fresh physical hashes/configuration/geometry and rollback capture,
exact physical display-binding review,then a fresh emulator reconstruction of
only that display change are required before a bounded hardware trial. No physical
FTP/deploy/test performed. Physical0101/video0093,0088rollback,immutable0.1.0 and
completed128GiB dump/recovery remain unchanged. Emulator upstream preparation and
new modes including1080i are separate work.
