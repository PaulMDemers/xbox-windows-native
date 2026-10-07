# Paired GDI drawing and paced append diagnostic

Fresh emulator-only children of the same settled FATX0101/video0093 fixture.
Same binary and startup in both:001 has one-byte mode0;002 has mode1. No driver,
registry, firmware, direct GPU access, debugger or physical action.
Both create the same private window and GDI objects on a separate thread. Mode0
pumps messages and sleeps without issuing the drawing loop. Mode1 fills eight
colored bands in a compatible bitmap, copies512x320 pixels to its own client DC,
and calls GdiFlush. It sleeps10ms per frame. GDI results and cleanup are checked.
No acceleration or pixel-perfect display correctness is inferred from API success.

The writer retains16 exclusive files,512 appends each, four seed offsets
401/3985/65425/270225, two explicit flush policies, two handle lifetimes. Same
known bytes and independent cold oracle as append-sequence. Both variants sleep1ms
every16 writes to permit scheduling; elapsed times are not performance benchmarks.
Opening/closing a handle may cause filesystem activity independently of explicit
FlushFileBuffers, so end-only means only the requested explicit flush policy.

Every case assigns a unique active epoch during its512-appends loop. A completed
frame counts toward overlap only if that epoch is unchanged and nonzero at the
start/end of the drawing calls. All16 drawing cases must show positive overlap;
control counts must be zero. Counters are atomic, and no drawing-thread file I/O
or per-append diagnostic I/O is used. Source checksums and exact post-call source
bytes, returned byte counts, flush/close results, live readback and independent
cold SHA/byte comparison remain separate evidence. Diagnostic records are emitted
after each sequence. Ready/join waits are bounded; incomplete/failed stages fail.

Build.ps1 uses the pinned RosBE compiler under the existing build lease. review.py
checks all static imports against owned NT5 DLLs and records source/build/PE hashes.
prepare-fixture.py creates one exclusive child; audit-before.py checks allocation.
Run.ps1 and supervise.py own one local xemu launch and normal-return observation.
trial.py collect collects once after cleanup; qualify.py retains strict failures.
verify-evidence.py verifies staged source/report hashes after both completed runs.
Use unique case001 then002; never repeat recorded launches or collections.

This load diagnostic is neither first-install reproduction nor a physical soak.
The settled parent retains its documented historical emulator device policy.
Original physical corruption and all earlier failures remain unchanged evidence.
