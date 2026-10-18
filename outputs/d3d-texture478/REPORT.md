# 478: Xbox D3D7 software texture control passes

Both default and explicit HEL cases pass using the exact PC479-qualified sample.
Each enumerates ten texture formats and selects an actual RGB32 format. An owned
8×8 texture renders through point filtering into a separate64×64 system-memory
target. Each case verifies4096 clear RGB pixels,576 texture-interior checkpoints
covering all64 distinct texels,1071 exterior pixels and palette-only values in
2449 boundary pixels. The256 source bytes remain exact after drawing. Eight raw
captures retain66,560 bytes across the two cases. Both processes exit0.

The single launch was accepted2026-10-18 at03:32:58UTC; UnleashX returned at
03:34:25UTC. The controller completed both cases and requested a normal restart,
supported by a fresh EventLog6006. The temporary startup hook was removed first
during collection. Original launcher, normal startup and protected720p settings
remain unchanged. No consoleC access, driver replacement or shared SDK changes.

Both actual11-module snapshots match double-read installed files and PE image
sizes. Ten runtime DLLs were pinned before launch. Five before/after hives have
clean headers and independent raw-value agreement; the inherited SOFTWARE DRM
type1004 limitation remains. No full FATX allocation scan was repeated.

Overall system qualification remains **false**. New system records614–620
include Ftdisk49 and two Application Popup26 records reporting rundll32.exe DLL
initialization failure because the window station is shutting down. The initiating
command is unknown. No new application-log records. No event was suppressed or
waived, and this pass does not resolve historical boot intermittency.

The unchanged20,398-byte sample SHA256 is
`0cf77cd741d0f066ee5a3fc4ad10508f3e6d8cb962c8a89c90fc19d6ee832f91`.
The namespace-only471 boot child SHA256 is
`15f27b3927d7df281c7536c3bae38b34c0df0948b233826a517043d1e2de3ae3`;
its Windows payload is byte-identical.104 actual-wrapper host cases model kernel
IO, and eight actual-dispatcher host cases model FTP; neither is hardware evidence.
The actual runtime above is separate.34 frozen package inputs were archived.
Each actual case rejects440 metadata and8704 pixel/source mutations (18288 total),
plus176 primary-report truncations. Original captures remain unchanged.

prepare-kit001 failed on a review-source anchor before build/deployment; the
failed script and record remain.002 completed generation. The failed477 PC
floppy and successful fresh479 PC result remain distinct; nothing was rerun or
requalified retrospectively. This physical case is closed, all owned processes
are closed, and no next test is queued.

This is a small offscreen software texture result. Exact raster/texel edges,
unused target X bytes, presentation, depth, blending, GPU acceleration, game
compatibility and useful game performance remain unqualified. Next: separate
depth and alpha-blending reference tests. Never relaunch/recollect/parent478.
