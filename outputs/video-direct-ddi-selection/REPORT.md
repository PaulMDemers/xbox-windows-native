# Authored direct-framebuffer DDI: ordinary emulator compatibility PASS

The0107 xwndir.dll now executes on NT5 and passes the bounded drawing workload.
Candidate001 and its existing Microsoft-framebuf control both passed all54cases
and162pixel stages, one normal shutdown/dashboard return, full allocation audit,
five structural hives and unchanged protected/payload hashes. Allocation counts
are325directories,6758files,326directoryclusters, zero errors/orphans. Neither
run has new warning/error/application events. The96MiB1536cluster pagefile and
its64-bit extent map are unchanged. No debugger or UI intervention in these two
passing runs. All owned processes are CLOSED; disks and metadata are retained.

The new candidate ran21:45:57 to21:47:35UTC on2026-10-07. Its exact read-only
DrvEscape response identifies revision107,1024x576x32,stride4096,2359296visible
bytes. This proves the authored driver executed; a desktop screenshot alone
would not. The qualified Microsoft control is video-direct-ddi/control001,
launched21:24:21UTC. Pair verification requires identical parent chains,
protected hashes, payloads and startup except the one-byte expected identity
marker and two known SYSTEM-hive selector values. Full logical hive comparison
confirms all other nodes/values unchanged. The original Microsoft DLL is intact.

No driver rebuild was required after the first trial. The initial fixture had
changed Services\XboxVnt5\Device0 but missed the bound GPU class\0001\Settings
InstalledDisplayDrivers. Windows kept framebuf resident; identity0 stopped that
probe before drawing. The failed attempt is preserved, including its900-second
timeout, post-timeout memory diagnostic and cold audit. Here both current-control-
set selectors name xwndir. Actual custom identity and54/162 completion validate
that correction without changing the display code or relaxing a gate.

Candidate SHA256:
019f5267a66cf0a018731d1a3db9f9c8ef737da5a7fbeb6965c1aa96948d0d68
Reconstructed source tree:
3c664be8842518eac9dd18d92f6a3e2f78d36f73

Source/build/host evidence is in ../video-direct-ddi: bounded32-bit framebuffer
contract, zeroed capability structs, mode-buffer bounds, failure unwind, read-only
identity escape;17 actual-surface.c host fault/geometry cases with ASan/UBSan and
leak checks, pinned NT5 imports and ten build source files. No shadow bitmap,
WC, GPU acceleration or new mode. The driver uses the existing permanentUC0106
provider; both passing runs logged the same successful shared mapping and44
trace records with no drops.

This is one bounded ordinary boot per display at1024x576x32. It does not qualify
all drawing APIs, direct scanout equality, cursor transitions, OpenGL/DirectDraw,
generic PnP, repeated boots or crash rendering with the new display. Existing
controlled-crash qualification belongs to the earlier Microsoft-display baseline.
No Xbox hardware speed claim or physical deployment. Emulator synthetic null-
device and01B0/01B4 unsupported-device policy remains inherited and explicit.

Preserve physical0101/video0093, original0088, immutable0.1.0 and completed128GiB
recovery evidence. Original111nonASCII physical corruption remains unresolved.
