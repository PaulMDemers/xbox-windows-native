# Elapsed rendering/upload diagnostic113

Evidence167 rejects general duplicate/full-screen uploads for measured rectangles;
actual compiled112 bulk copy already REP MOVSL. It does not attribute fill/upload
slowness to rendering versus video memory. This kit adds observation only, leaving
ROP/owner selection/copy/clip/upload/return semantics unchanged. No store optimization.

Build matched113 control(profileOFF) and candidate(ON), same reviewed112 parent
tree, clock calibration128 back-to-back pairs in both. Frequency/monotonicity,
overhead minimum/maximum and explicit error/overflow flags come from actual NT5
EngQueryPerformanceCounter/Frequency. No guessed timer or failed-query fallback.
Snapshot 0x58574433,128bytes/version113; original112 identity/stats unchanged.

Measure EngBitBlt, EngCopyBits, upload copy-body and complete upload-wrapper elapsed
ticks. Queries outside membership lock; accounting/snapshot inside existing lock
protects32/64bit fields. No lock held across an engine call/copy/query. The lock
does not replace GDI's submitted surface/PDEV lifetime or rendering serialization.
Elapsed times include preemption/interrupts; wrapper includes nested counter-lock
overhead. Device-global counts/times include background. Never label exclusive CPU
time or subtract calibration minimum as if it were a known constant per call.

Control still has bookkeeping/locks/calibration; candidate comparison isolates
added body clock queries, NOT total profiler overhead versus untouched112. Require
that distinction and later untouched112 comparison before optimization claims.

New v5 user probe retains167 livecopy/overlap/coherence and adds explicit independent
black/white expectedRGB readback plus pattern/DIB checks. Snapshots outside timed
loops. Same166 one-shot launcher, unique children/namespace, frozen sources/binaries,
actual import/compiled residency checks and full cold allocation/hives/protected/
event audits. Reject every popup type. Debugger169's no-popup result does not cure
167/168. Strict Ft49 remains failure; no physical eligibility from debugger evidence.

Emulator ONLY; no physicalFTP/deploy/test. Preserve installed0101/video0093,0088
rollback, immutable0.1.0 and failed evidence.20GiB guard unchanged.
