# Diagnostic113 compiled and observed; no optimization or physical promotion

New113 adds synchronized elapsed counters for EngBitBlt, EngCopyBits, upload
copy body and complete upload wrapper to reviewed112 source. Rendering/ROP/clip/
ownership/copy algorithms and112 identity/stats ABI remain unchanged. New128-byte
version113 read-only escape0x58574433; no user pointers/configuration writes.

Both builds use source tree5278872003703e4d8948e26fb754544ec7777fe3 and differ
only in XWN_BODY_PROFILE OFF/ON. Control SHAe151223012498b65ad80b89f27fd80d5fbc074485b91a5fb75dd0be565b5abb0;
candidate SHA938100484670ed1ee35fb28ebce6e98564b3b3a54ea92e2cd7db47e6854b275e.
Actual NT5 imports checked against captured Win32k, every new helper and selected
render/upload function in resident .text. The OFF clock stub returns64bit zero;
ON initializes sentinel and calls the actual EngQueryPerformanceCounter import.
Frequency/calibration done in both;128 back-to-back pairs, errors/overflow explicit.
Existing membership lock protects accounting/snapshot only, never held across
clock queries/render/copy; GDI's PDEV/surface lifetime contract remains necessary.

Actual arithmetic header passed4142 ASan/UBSan checks, including64bit boundaries,
regression/invalid input, overflow saturation and disabled mode. Initial clang
command unavailable, preserved host-tests001.py; GCC performed the real checks.
Build001 stopped BEFORE compilation at exact source hash guard: Windows text
append created mixed line endings in3 files; unified patch reproduces LF.
Inputs retained underbuild001-expected and WSLvideo-body-timing170-001, precise
audit inbuild001-integrity-failure.json. Fresh002 normalized source hashes exact,
compiled matched drivers. Unused static-header-function compiler warnings retained.

New v5 helper, actual NT5 imports verified, exact unchanged166 one-shot launcher.
Adds two independently expected black/white readback checks to pattern/copy/
overlap and existing RAM/scanout checks; timing snapshots outside timed loops.
First171 host validator blocked control before any Windows launch; preserved.
Fresh ordinary172 control/candidate both completed30 live expected pixel checks,
25 loops,50 fullscan coherence checks, normal shutdown/dashboard, full cold clean
allocation/hives/protected hashes. Runtime clock1125000Hz,128 calibration pairs,
errors0/overflows0/monotonic/read accounting PASS. See172 report/pair-analysis.

Driver-review.json was created BEFORE runtime and correctly retains its original
clock_runtime_qualifiedFALSE;172 provides subsequent functional clock evidence.
Strict results remainFALSE (Ft49 plus1shutdown installer popup in EACH ordinary
run). No physical deployment, release, FPS or optimization claim. Existing
physical0101/video0093,0088 rollback and immutable0.1.0 preserved.

Interpretation correction: frozen design says OFF isolates clock queries only.
ON also updates tick/read counters/64bit arithmetic, so comparison measures
enabled profiling increment. Both retain common bookkeeping/locks; no untouched
112 overhead baseline. Direct DDI calibration does not cover the full profiler
wrapper; never subtract its minimum as a known per-operation cost. Preserve
all frozen wording and refer to172/INTERPRETATION.md rather than editing history.
