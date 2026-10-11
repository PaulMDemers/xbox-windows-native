# Observe actual surface invalidation callers before changing ownership

The250 source review found the prior82/83 telemetry only at flush_surfaces,
which had no surface entries in the actual run. New257 instruments all five
callers before their existing download/invalidation work, plus common entry.
The first bounded run distinguishes which callers actually see draw_dirty,
download_pending, upload_pending, CPU eviction and pending primitives, and whether
CPU-read/write callbacks occurred. It does not prove latest pixel preservation.

No renderer disposal, download, guest/host ownership or device policy changes.
Scalar events only: no new GL calls or content writes. This is a diagnostic xemu
build, not ordinary emulator/physical qualification or a video speedup. If clean
entry follows dirty-before-download it establishes observed state transition,
not independently correct bytes. Retain missing coverage; no blind repeats.
Next content test must use independently controlled pattern and actual alias
activity at identified lifetime boundary, preserve latest CPU data, and retain
all prior ownership refusals. Same exact250 fixture/workload and bounded host
cleanup, full cold audits, pinned source and resource leases required.
