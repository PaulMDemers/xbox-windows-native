# Area, rectangle count and row-copy cost on unchanged RAM0112

One ordinary emulator child uses the qualified0112 display and inherited shared-UC
miniport/HAL/storage/network chain. No driver code/cache/device-policy changes.
Three pixel areas:64x64,192x96,384x192. Five layouts per area:one contiguous
rectangle,4/16 horizontal strips,4/16 vertical strips. All equal-area groups
have exactly equal uploaded bytes per draw. Horizontal strips preserve total
row-copy count; vertical strips multiply row-copy count. Gaps prevent merging.
45samples,3rotated repetitions. Memory DIB and primary phase order alternates.
Each PatBlt alternates two solid brushes, GDI batching limit1, final GdiFlush.
The memory phase is a rendering/API baseline, not exact subtraction of uploadcost.

Warmup8 operations,then powers-of-two32..65536 calibration until at least500ms.
One measured batch at that count; require final>=250ms for timing qualification.
Calibration/warmup are excluded from measured counters/time. No file writes,stats
escapes,host cold reads,preparation or debugger pauses inside measured batches.
File persistence and pixel readback occur after both phases. Time QueryPerformance-
Counter and GetTickCount,record actual frequency,8192 consecutive increments,
3Sleep200ms crosschecks and unchanged final frequency. Crossclock tolerance is
max31ms/10%; timing failure remains distinct from functional pass,never waived.
QPC increment is observed call-to-call resolution including overhead,not asserted
hardware clock precision. Batch cost includes USER/GDI/rendering/upload overhead.

Use existing exclusive xemu resource and hold build lease for entire runner.
Local Invoke-Exclusive differs only in resource mode and original script root.
Finish preparation beforelaunch and cold audit aftercleanup. This isolates other
cooperative Xbox builds/emulators,not all unrelated host activity. No physical
FPS/throughput claim or cache/MMX/SSE change follows from these measurements.
No simultaneous test,driver source changes,forced system popup dismissal or
settings changes. Raise only owned fullscreen parent and require visible ROI.

Save45 CPU/DIB references and45 actual primary readbacks,768x384 each. Independent
host geometry/pattern oracle,strict per-batch calls/uploadcounts/bytes,quietcounter
checks,normalshutdown/dashboard,fullallocation,5hives,protectedfiles,startup,
pagefile/configuration and strict event deltas. Existing synthetic null/unsupported
policy stays explicit. Preserve any failed preparation/launch/calibration separately.
