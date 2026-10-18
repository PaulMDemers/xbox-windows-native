# PC480: scoped D3D7 software depth control PASS

One fresh PC fixture boot completed both default and HEL processes, then restarted
normally. QEMU exited0 at2026-10-18 03:52:13UTC without host quit/kill or watchdog.
No physical access in this case. Never relaunch, recollect or parent this fixture.

The original sample is20,283bytes, SHA256
`00f6487c474420a2b84d60381d2915621c047e33eb2c3b27adc2c2ecd99c9d2f`.
Pinned RosBE build has no compiler warnings; NT5 imports match the installed
exports (controller24/sample26). Both actual RGB software devices enumerate two
depth formats and select the first depth-only16-bit format. The other format has
stencil bits and is retained in the report, not silently selected.

All five64x64RGB32 captures per process pass: clear, far/near, near/far,
depth-disabled, and depth-cleared-to-zero. Near green wins in either enabled draw
order; far magenta wins with depth disabled; zero-clear rejects both under LESS.
Ten captures total163,840bytes. Each image has561 safe interior and2199 exterior
checks, with1336 raster-edge-zone pixels limited to the prescribed colors. The
blank/zero images are entirely background. Exact raster edges, X byte, depth
precision, stencil, presentation, speed, hardware acceleration and games remain
unqualified. API success alone is not the pixel result.

Actual attached surface identity/format/caps, prescribed vertices, state changes,
HRESULTs and cleanup are complete. Device/depth/target/DD releases return0, depth
is explicitly detached, and the runtime module snapshot contains11 modules.
Actual selected module paths/PE image sizes match cold file bytes. This is not a
trace of previously unloaded modules or a general memory-leak qualification.

Three host tests include20,480 synthetic pixel mutations and independent depth
failure discriminators. Actual records reject513 metadata plus20,480 pixel
mutations per process:41,986 total. Original captures remain unchanged.

The fresh read-only1,474,560-byte FAT12 floppy passes independent directory/FAT/
chain/content checks before preparation and again at launch.39 host negatives
include the historical malformed477 image;477 remains failed and untouched.
Source404 is the reusable NTFS seed, not an executed test child.

Cold audit enumerated6491files/309directories. Five hives pass header/clean/raw
agreement checks; protected OS binaries, source and floppy are unchanged.
Independent NTFS-3G readback agrees on31 files, unmounts cleanly and leaves the
disk unchanged.149 exact inputs archived privately. New selected system events
are6006/6009/6005 with no error/warning in this delta. This does not establish a
full NTFS allocation audit or whole-system qualification; the inherited SOFTWARE
DRM typed-value limitation is retained. All owned processes closed.

Actual evidence: [runtime](runtime-review001.json), [cold](ntfs-cold1-002.json),
[independent reader](independent001.json), [mutations](actual-controls001.json),
[final review](final-review.json). Images, binaries and Windows files stay private.
