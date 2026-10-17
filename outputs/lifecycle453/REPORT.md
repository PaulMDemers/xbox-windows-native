# NT5 PC bounded lifecycle control PASS

Default and HEL each completed8 warm-up and64 measured iterations with two
128x96 RGB32 system-memory surfaces. Every measured source/destination byte
matched the independent oracle:6,291,456 bytes per backend,12,582,912 total.
All288 surface releases across warm-up and measured iterations returned0.
Both processes exited0. Commitment growth after warm-up was0 under the declared
1MiB budget; this is finite process accounting, not proof of leak freedom.

Each process refused a malformed descriptor with no returned surface, then
created valid surfaces. Three calling-thread focus transitions were acknowledged
while the first measured pair remained allocated. Subsequent pixel readbacks
matched. IsLost always returnedDD_OK; actual lost-surface/Restore behavior is
NOT qualified. There was no mode change:640x480x16 throughout, no primary or GPU.

The sample compiled warning-free with pinned RosBE/GCC8.4. Its27 static imports
and the controller's24 imports match owned NT5 exports. PSAPI was independently
extracted read-only from the pinned owned source; the actual PC manifest matched
its hash. The fresh404 child completed normal guest restart, QEMU exit0, no host
quit/kill/deadline. Five hives are clean with raw-value agreement; protected OS
binaries, source and floppy remained exact. Cold enumeration6483files/309dirs:
8adds,0removals,15changes. Independent NTFS-3G extraction agrees on19 files and
unmounted cleanly.4,718 actual-result mutations were rejected.147 inputs archived
and231 private files rehashed. All owned subprocesses closed.

The initial kit generator changed inherited launch-guard line endings and failed
its byte hash check before preparation. That source and failure are preserved;
the exact inherited guard was restored before preparation/preflight/launch.
The full146-dependency preflight completed before launch. No repeated attempt.

Evidence: [design](DESIGN.md), [build](sample-build001.json),
[imports](binary-review001.json), [runtime](runtime-review001.json),
[independent reader](independent001.json), [negative controls](actual-controls001.json),
[closeout](final-review.json), [generator failure](generator-failure001.json).
The physical comparison uses a distinct454 namespace; no console result follows
from this PC pass. No full NTFS allocation audit, GPU, D3D or game qualification.
