# Equal-area transfer measurements on RAM0112

One ordinary emulator boot completed all45samples/90phases, with13,271,040 exact
live pixels,45 exact cold reference files and45 matching cold primary RGB planes.
The driver was unchanged. Strict workload, timing, event and integrity gates pass.
No physical access or debugger. This is three repetitions per geometry in one boot,
not independent-boot performance reproducibility or physical speed qualification.

## Results

Median primary-surface batch cost in microseconds per PatBlt, including GDI/API,
rendering and upload. Equal-area layouts upload exactly the same bytes per draw.

| Area | Solid | Horizontal4 | Vertical4 | Horizontal16 | Vertical16 |
| --- | ---: | ---: | ---: | ---: | ---: |
|64x64|23.18|182.78|38.66|195.77|65.91|
|192x96|67.69|1652.77|92.28|1676.77|174.73|
|384x192|8489.07|13482.07|7153.65|13742.86|4358.69|

Horizontal4 and horizontal16 differ only about1.5-7.1% in median cost despite
four times as many upload calls. At192x96, horizontal16 is9.60times slower than
vertical16, despite equal bytes and equal16 upload calls; vertical16 performs
16times as many row copies. Thus total bytes, rectangle count and row-copy count
alone do not explain the measurements. A positive constant per-rectangle or
per-row model is insufficient for these cases. This does not identify a cause.

The layouts also change addresses and spatial extent: horizontal strips spread
over more rows, vertical strips across more columns. They do not isolate upload
setup from address/layout effects. DIB memory baselines are retained in
analysis.json, but cannot be subtracted as a pure framebuffer-copy time.
Large vertical16 primary samples ranged3903-7081us, and the first medium
horizontal16 sample was908us versus1677/1765us later. Keep all samples; do not
select the fastest repetition. No driver optimization follows solely from this.

## Timing and ownership

Calibration doubles32..65536 draws until>=500ms; every final batch meets>=250ms.
QPC frequency1,125,000 remained unchanged.8192 observed reads had no zero or
negative increments, minimum1tick, maximum9120ticks. Minimum observed GetTickCount
increment15ms. Three sleep checks and all90 batch cross-clock checks meet the
predeclared max31ms/10% tolerance. Read-to-read increments include call overhead;
the1tick minimum is not a claim of absolute clock precision or physical speed.

Actual xemu mode was exclusive. While it ran, direct acquisition of both existing
build and xemu lockfiles failed as expected. The build lease enclosed launch,
dashboard return and cleanup. Preparation completed before launch; no host builds,
cold reads, debugger or fixture creation ran during measurement. This excludes
competing cooperative Xbox work, not all unrelated host processes. analysis.py
checks the lease identities and timeline in addition to the frozen verifier.
Eight synthetic isolation/completeness mutations are rejected by test-analysis.py.

## Persistence and provenance

267,200 measured primary BitBlt callbacks; exact upload counts/bytes in every
batch and quiet counters before batches. Other hooks remain unqualified by this
probe. Normal shutdown and dashboard return; no warning/error or application
event delta. Complete allocation327directories/6851files/328directoryclusters,
zero errors/orphans; five structural hives, protected binaries, startup,
configuration and96MiB/1536cluster pagefile unchanged. Coherent driver readback
does not independently verify physical scanout.

Pinned probe139 and display0112; display SHA256
ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8.
The prepared parent contained0110, so pe-review.json's driver_changed=true means
replacement relative to that parent; this turn introduced no new driver source
or binary. Inherited emulator null/unsupported-device policy remains explicit.
Shared-UC0106, FATX0103/HAL0102/NVNet0104/ATAPI0105 and restored HidServ unchanged.

Single launch accepted2026-10-08T04:47:26.924971UTC; dashboard returned04:52:22.749015;
cleanup04:52:23.0297867. Preparation26706, runner57733, supervisor24708, audit62974
and closure/verifier5118 all CLOSED. Never relaunch or recollect candidate001.
Private disk remains work/runs/nt5-vexclusive-candidate001/hdd.qcow2; hash and full
input/source pins are in candidate001/closure.json and preflight.json.

Preserve video-transfer-cost/candidate001: host path resolution failure before
Windows, no timing result. Also preserve its warning-as-error compile rejection.
The new canonical-root/assertion and backing-path preflight fix only the harness.
Physical0101/video0093,0088rollback, immutable0.1.0 and prior128GiB evidence intact.
