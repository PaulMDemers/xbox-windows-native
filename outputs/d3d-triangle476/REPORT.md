# 476: D3D7 RGB software triangle passes on the Xbox

Both default and explicit HEL cases created the actually enumerated RGB software
D3D7 device, cleared an owned64x64 RGB32 system-memory target, and drew the fixed
pretransformed triangle. Each process exited0. Each independent oracle verified
4096 clear pixels,561 interior pixels and2199 exterior pixels. The1336-pixel
boundary band contains only background/triangle colors; exact edge coverage and
the unused X byte are not qualified. Four complete captures retain65536 raw bytes.

Single launch accepted02:59:15 UTC on2026-10-18; dashboard returned03:00:43 UTC.
The controller completed both cases and requested a normal restart. Fresh
EventLog6006 supports that shutdown. The temporary hook was removed first on
collection; original launcher/startup/protected720p configuration remain exact.
Console C was not accessed. All owned subprocesses are closed; no test queued.

Both11-module live snapshots include D3DIM700.DLL and agree with actual installed
file hashes/PE image sizes. Ten runtime DLLs were pinned before launch, then
read twice after shutdown; the owned sample's collected bytes match PC474.
This snapshot does not account for helpers already unloaded before capture.

Five before/after hives are clean with valid headers and independent raw-value
agreement; inherited SOFTWARE DRM type1004 limitation remains. New system
records608..613: Ftdisk49, EventLog6009/6005, Tcpip4201, Application Popup26,
EventLog6006. The popup reports rundll32.exe DLL initialization failure because
the window station is shutting down. Its initiating command remains unknown.
No new application-log records. Strict overall qualification remains FALSE;
no event was suppressed or waived, and no full FATX scan was repeated.

The earlier475 attempt returned before producing Windows/sample evidence and
remains a failure. This successful fresh attempt does not resolve boot
intermittency. Both boot preparation records alone stop short of paging/handoff
proof; the actual sample receipts and fresh Windows events supply this run's
separate Windows evidence. Original failures/rollbacks are preserved.

The triangle executable is byte-identical to qualifiedPC474:
`eee41bde74531434f777b5b0bd98784d0e56d5e992c7d541c91fe5f05848be59`,18070bytes.
The namespace-only boot child keeps the471 Windows payload byte-exact; its SHA
is `1389e4823a605a3d11f69dda93582008c2911c813e7a0b17cea162258563548a`.
104 actual-wrapper paths with modeled kernel/IO and8 modeled-FTP dispatcher
paths pass.31 frozen dependencies archived.16924 actual report/pixel mutations
and176 actual primary-report truncations are rejected. All originals rehashed.

This is software rendering, not GPU acceleration. No textures, depth, blending,
presentation, game compatibility or useful game performance is established.
See [design](DESIGN.md), [runtime](runtime-review001.json),
[module provenance](module-review001.json), [controls](actual-controls001.json),
[closure](final-review.json). Do not relaunch/recollect this consumed case.
