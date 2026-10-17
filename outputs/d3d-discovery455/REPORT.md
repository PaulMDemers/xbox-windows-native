# NT5 PC Direct3D7 inventory PASS; software RGB device found

Both default and explicit HEL paths expose IDirect3D7 and enumerate one device:
Microsoft Direct3D RGB Software Emulation, named RGB Emulation, GUID
 a4665c60-2673-11cf-a31a-00aa00b93356. Its reported caps are1361, render-depth mask3840,
depth mask1024, maximum texture1024x1024, texture-op mask30975,8 blend stages and8
simultaneous textures. Hardware rasterization and hardware transform/lighting
flags are clear. These are actual runtime declarations, not CreateDevice or draw
results; no native acceleration or game compatibility is claimed.

Each236-byte descriptor is fully retained and joined to scalar GUID/capability
records. Both descriptors match byte-for-byte.566 actual scalar/descriptor/length
mutations were rejected. The public checker distinguishes available, empty and
unavailable inventories; synthetic tests cover capacity, duplicates, truncation,
classification, cleanup and every binary byte.12 actual compiler assertions verify
structure size/field offsets and hardware-bit constants against pinned headers.

The sample and controller compiled warning-free, with21 and24 static imports
matching owned NT5 exports. One fresh404 child used completed150-input preflight
before launch, unchanged640x480x16 mode and pinned DirectDraw. Both processes
exited0; normal guest restart ended QEMU with exit0, no host quit/kill/deadline.
Five hives are clean/raw-agree; protected Windows binaries, source and floppy exact.
Independent NTFS-3G readback agrees and unmounted cleanly. All owned processes
closed. See final-review for archived dependencies and private capture hashes.

Two prelaunch metadata failures remain preserved: layout001 compiled successfully
but its post-compile header comparison failed on stddef.h; review002 incorrectly
expected one additional header. The dependency file actually includes both SDK
and GCC stddef.h. Read-only review003 pins both, preserves all originals and does
not repeat compilation. This did not change the sample or any runtime fixture.

Evidence: [design](DESIGN.md), [build](sample-build001.json),
[layout review](layout-review003.json), [failures](layout-failures001.json),
[runtime inventory](runtime-review001.json), [negative controls](actual-controls001.json),
[independent reader](independent001.json), [closeout](final-review.json).
No full NTFS allocation audit, complete live helper-module trace, CreateDevice,
rendering, scanout or physical Xbox qualification follows from this PC result.
