# Independent full-desktop GDI scanout diagnostic

Fresh immutable child, exact same probe121/source/display bytes as ordinary
video-gdi-coverage4. Capture26 raw physical frames plus independent DIB memory
at actual XwnGdiShot boundaries. Require runtime reference FNV and bounded GDB
first/last64-byte agreement; after shutdown require complete SHA256 agreement
with cold reference files. Compare all2,555,904 RGB pixels. Preserve mismatches.

Reuse the repaired observer with actual entry demand-fault deferral, per-process
filtering and thread/frame pairing. Pin actual kernel/probe/API and full relocated
display text, bound600seconds, remove every breakpoint and resume on all paths.
All ordinary cold/event/workload/reference-counter requirements still apply.
Debugger qualification is separate; no hardware/performance claim or driver change.
