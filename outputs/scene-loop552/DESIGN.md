# 552: bounded rendering in one software D3D7 context

Fresh PC control; no console access or boot diagnostic. Keep 550/551 closed.
One process per backend; five existing scene cases, 32 additional frames each.
Resources remain allocated across all 160 frames. Check each case's endpoint
using the existing independent geometric and GDI oracle, and verify texture
bytes and final COM releases. This is not per-frame image proof or leak freedom.

QPC intervals separate render API/state validation plus target lock completion,
CPU readback/native conversion, and primary Blt plus GdiFlush. No report writes,
binary captures, sleep or message pumping inside those intervals. Capture and
validate endpoints outside timing. QueryPerformanceFrequency is recorded; raw
64-bit counter values and coarse ticks retain clock cross-checks. No FPS, GPU
scanout or game-performance claim. Each batch has a 30-second tick deadline;
the private runner bounds the entire owned process to 180 seconds.

Load PSAPI from the system directory and record working set, commit and peaks
before graphics allocation, before/after each batch and after graphics release.
Do not require exact return to baseline: allocator/runtime caches can persist.
Reject failed queries, impossible counter relations and missing/unknown fields.
Independent host tests must reject malformed timing/memory data before a VM.

API contracts: Microsoft QueryPerformanceCounter/QueryPerformanceFrequency and
GetProcessMemoryInfo documentation; NT5 imports independently checked against
the exact fixture DLLs before launch. Modern documentation is not NT5 evidence.
- https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancecounter
- https://learn.microsoft.com/en-us/windows/win32/api/profileapi/nf-profileapi-queryperformancefrequency
- https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo
