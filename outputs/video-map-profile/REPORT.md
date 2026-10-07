# Matched video mapping comparison

Both ordinary emulator cases are CLOSED and strict PASS. Each completed all
54 timing cases and 162 full RGB pixel verification stages, restarted normally
and returned to the dashboard. Each cold audit found 324 directories, 6755 files,
325 directory clusters, zero allocation errors/orphans, five structurally valid
hives, unchanged protected binaries/payloads and zero warning/error/application
event deltas. Pagefile chain and inherited device configuration were unchanged.
No debugger, interactive input or physical-console access occurred.

The candidate actually mapped reserved RAM0x03C00000..0x03FFFFFF. Its 73-record
trace includes present first/last page PTEs with UC cache type; known loader
alias endpoints were absent. This is not an exhaustive alias inventory.
See candidate001/mapping.json and pair-review.json, including source/fixture pins.

Only the protected miniport binary differs between matched fixtures. Control
is0093 SHA3e74a5c3..., candidate is existing0096 SHAe8021879...; Microsoft framebuf,
probe12f06826..., startup, initial hives, trace seed and all storage/network
drivers are identical. No new driver was built.0096 includes mapping ownership
and read-only mapping instrumentation in addition to the address-path change;
this is not a comparison of one isolated instruction.

|768x384 operation|Aperture0093 ms|Reserved RAM0096 ms|
|---|---:|---:|
|Fill|69|66|
|DIB upload|69|66|
|Screen readback|7.89|7.14|
|Screen overlap|75|72|
|RAM overlap plus upload|72|69|
|RAM overlap only|0.574|0.549|

These are medians of three rotated rounds. The large-copy difference is small,
and memory-only copies show a similar relative shift. Smaller cases are mixed.
There is no convincing performance basis here to promote direct mapping.
The result does not rule out a difference on physical hardware, whose historical
read/write timing balance differs from xemu. Candidate preparation/cold reads
overlapped part of the control run; both used the shared functional emulator
slot. They are not isolated performance benchmarks or window-drag FPS.

The predecessor fixed-driver profile likewise found that RAM copy plus upload
retained most of the screen-copy cost. A cached shadow driver would still need
correct upload, cursor, clipping, raster operation and lifecycle behavior.
Do not infer its benefit from memory-only copy speed.

No prototype promotion or hardware deployment follows. Generic0096 PnP
stop/remove consumer quiescence and restart remain unqualified. The exact GDI
self-readback checks do not independently verify GPU scanout. All historical
popup, initialization and host-launch failures remain separate failures.
