# Row-position sensitivity reproduced with unchanged RAM0112

The single ordinary exclusive emulator run passes strict correctness, persistence,
events and timing gates. Moving an identical192x96 solid rectangle down160rows
increased median primary PatBlt cost47.996times, with essentially unchanged memory
DIB cost. Moving it right128pixels changed little. The source and destination
shapes move together; bytes, upload count, row count and shape remain identical.
This is an observed position sensitivity, not a proven TLB/cache/scanout cause.

## Translation controls

Median microseconds per draw across three rotated repetitions in one boot:

|Shape|Origin|Memory DIB|Primary surface|
|---|---|---:|---:|
|Solid|(0,0)|29.15|72.50|
|Solid|(128,0)|29.07|71.24|
|Solid|(0,160)|29.36|3479.85|
|Horizontal16|(0,0)|30.89|1553.65|
|Horizontal16|(128,0)|30.80|1708.57|
|Horizontal16|(0,160)|30.90|3204.38|
|Vertical16|(0,0)|85.50|179.94|
|Vertical16|(128,0)|83.97|177.94|
|Vertical16|(0,160)|87.64|3201.14|

Every row copies73728bytes. Solids upload one rectangle with96 row copies;
horizontal16 uses16rectangles/96 row copies; vertical16 uses16rectangles/1536 row
copies. All actual counter deltas match. Translating down multiplies primary
median cost48.00x/2.06x/17.79x respectively; memory ratios1.007x/1.000x/1.025x.

This is not only a median artifact: all three lower solid samples(3039.70,
3479.85,3493.81us) exceed all top solid samples(120.82,72.50,71.96us).
Keep the warm-start and other variability. Horizontal16 shifted right ranged
1022.42-1751.73us. We have no independent-boot repeat of this translated workload.
Memory and primary cost must not be subtracted as pure framebuffer bandwidth.

## Fixed-height width sweep

All solid shapes below have height96, origin(320,64), one upload and96 row copies.
Width changes bytes per row; it does not change the number of touched row starts.

|Width|Bytes/draw|Memory median us|Primary median us|
|---:|---:|---:|---:|
|64|24576|14.01|638.04|
|128|49152|22.41|1095.83|
|192|73728|27.62|1542.43|
|256|98304|36.37|3045.95|
|320|122880|43.30|4160.79|
|384|147456|49.89|5176.26|

The primary curve is not explained by a constant setup cost plus the number of
rectangles. The width256 jump is a lead, not proof of a copy-instruction threshold.
The existing width sweep is at a different origin than the translation baseline;
do not turn a cross-table difference into a width-only comparison.

## Static source leads and limits

source-review.json pins the inspected driver and local borrowed xemu source.
XwnUploadBox copies each row with memcpy using ScreenDelta on both sides. At the
verified4096-byte pitch, advancing one row changes the virtual page. The inspected
TCG implementation indexes its software TLB from virtual page and a size mask;
the VGA path snapshots dirty RAM and checks scanlines. These are plausible
address-sensitive paths, but no runtime TLB misses, translation size, copy target
addresses or actual VGA call stack were captured. The borrowed source is not
asserted to be an exact pristine tree; its base marker and individual hashes are
retained, and the loaded emulator binary is independently pinned. Do not patch
the guest driver or emulator solely from this static inspection.

## Qualification and provenance

45samples/90phases,13,271,040 exact live pixels;45 reference files match the CPU
oracle byte-for-byte,45 actual cold RGB readbacks match. All changed pixels fit
in the verified768x384 ROI; screen1024x576. Actual89,856 measured BitBlt callbacks,
exact per-phase upload counts/bytes, quiet pre-batch counters. Other hooks are not
qualified by this probe. Coherent driver readback is not independent scanout proof.

QPC1,125,000 unchanged;8192 reads,zero zero/negative increments,minimum1tick,
maximum13106ticks. Observed GetTickCount minimum15ms. All three sleep crosschecks
and90 measured batches meet unchanged clock tolerance and>=250ms duration gates.
500ms calibration target, no guest file writes inside measured batches. Exclusive
xemu and held build leases verified by acquisition conflicts and full timeline.
No host build, preparation or audit during timing; unrelated host load is not
excluded. Eight synthetic isolation/completeness mutations rejected;754geometry
checks and eight protocol failure checks passed before launch.

Normal shutdown/dashboard, no warning/error or application event delta. Full
allocation327directories/6851files/328directoryclusters,zero errors/orphans;
five structural hives, protected binaries, startup/configuration and96MiB/1536
cluster pagefile retained. Strict timing qualification is ordinary emulator-only.

Probe140 SHA2563d1a5f7baecd43cfa5fe74d96531626c31a67013c9081622b89250020b1c9b1d;
unchanged display0112 SHA256ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8.
pe-review's driver_changed=true refers to replacing0110 in the prepared parent;
no new display binary was developed in this turn. Shared-UC0106, FATX0103/HAL0102,
NVNet0104/ATAPI0105, restored HidServ and inherited emulator-only null/unsupported
device policy unchanged. Physical0101/video0093,0088rollback,immutable0.1.0 and all
earlier evidence preserved. No physical FTP, deployment or testing.

Preparation52776,runner70466,supervisor41487,audit46083 and verifier92378 CLOSED.
Single launch accepted2026-10-08T05:00:37.931577UTC, dashboard05:05:35.842531,
lease closed05:05:36.1751498. Never relaunch/recollect candidate001. Private disk
work/runs/nt5-vposition-candidate001/hdd.qcow2 is pinned in closure.json; source,
fixture, compiler, emulator and interpretation pins remain in this kit.
