# 553 PC sustained scene: scoped PASS; QPC durations unqualified

Two software D3D7 contexts (default and HEL) each completed 2,560 frames in five
512-frame batches, holding the same resources throughout. All ten independent
batch endpoint checks pass: geometry, textures, depth/order, native conversion,
clipped window presentation and source preservation. Every frame is submitted
and checked for API success; only the five endpoints per process are image
checked. Texture bytes and final COM releases pass. This is not game or GPU
qualification and does not establish long-run leak freedom.

The new sample compares the high-resolution counter against two longer coarse
intervals before rendering. Both processes report a frequency of 26,529,150,000 Hz,
but the 250 ms intervals convert to 34.1–34.9 ms and the 1,000 ms intervals to 141.2–143.0 ms.
Both comparisons fail. The checker explicitly returns null QPC phase durations;
it does not repair/rescale the frequency. The underlying clock discrepancy is
not diagnosed. These are guest-clock comparisons, not an external time standard.
552's earlier frozen frequency-gate failure remains closed and unwaived.

Independent GetTickCount phase deltas are retained below. They include counter
call overhead and are quantized; zero would mean unresolved, not zero work.
Rendering covers the API/state sequence and target lock completion. Upload covers
CPU target readback and native conversion. Presentation covers primary Blt plus
GdiFlush, not physical scanout. Deliberate sleeps, report writes and binary
captures are outside these measured phases. They are not FPS or Xbox speed.

| Mode | Scene | Batch ms | Render ms | CPU upload ms | Present API ms |
|---|---:|---:|---:|---:|---:|
| default | 0 | 453 | 359 | 32 | 62 |
| default | 1 | 578 | 314 | 46 | 218 |
| default | 2 | 563 | 282 | 77 | 204 |
| default | 3 | 297 | 109 | 125 | 63 |
| default | 4 | 453 | 233 | 78 | 142 |
| hel | 0 | 406 | 313 | 31 | 62 |
| hel | 1 | 454 | 314 | 61 | 79 |
| hel | 2 | 453 | 310 | 32 | 111 |
| hel | 3 | 265 | 140 | 93 | 32 |
| hel | 4 | 391 | 344 | 16 | 31 |

Commit was 647,168 bytes before/after each batch in both processes. After graphics
release it was 581,632 bytes, a 65,536 byte reduction, while remaining 364,544 bytes
above the pre-graphics snapshot. Windows/GDI objects and PSAPI still exist then;
runtime allocations and caches are not isolated. Do not call that retained delta
a leak or use the steady samples as long-run leak proof. Reported peak commit
was 663,552 bytes. Peak working sets were 2,056,192/2,060,288 bytes.

One new overlay of the original 404 NTFS source, one VM boot and one runner
invocation. Both child exits zero, normal restart request, no host stop/deadline,
cold EventLog 6006 delta one. Original seed/floppy and protected OS binaries stay
exact. Two independent cold readers agree; twelve live/cold modules per process
match. Five hives audited with inherited typed SOFTWARE DRM limitation; no full
independent NTFS allocation-bitmap/ownership audit. Five host tests and 616 actual
loop-metadata mutations pass; 38 floppy negatives pass. 156 inputs archived privately;
all owned processes/mounts closed. Never rerun/recollect/parent 553.

The public builder compiles the same source with the same pinned compiler;
rebuilt bytes have no separate runtime claim. A post-close checker-only fix
returns the raw input report's hash instead of its normalized inherited report
hash.554/checker-review002 compares both saved results (only that hash changes)
and reruns the five host tests. Its first comparison failed on Python tuples
versus JSON lists; that failed review is retained. No guest rerun or recollection.
Original 553 source/checker/tests remain in frozen-source001 for reproduction.

Matched 554 physical preparation is separate and awaits a new cold-start answer.
No console write or launch occurred in552/553; boot diagnosis remains tabled.
