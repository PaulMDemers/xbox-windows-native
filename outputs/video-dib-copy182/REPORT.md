# Bounded DIB114: exact-copy evidence, no upload benefit demonstrated

Original114 implements a conservative standard32bpp DIB SRCCOPY-to-RAM path on
112; scanout, ownership, surface allocation, cache attributes and modes remain
unchanged. Shared geometry passed321785 ASan/UBSan checks with30000 independent
byte-oracle/redzone cases, signed rows/clipping/alias/overflow. Fresh matched
RosBE builds use treeee6556aa1cbb3a23f7ce4bef0f15cc489cc1fef8 and differ only in
XWN_DIB_FASTPATH OFF/ON. Actual NT5 imports and resident adapter/surface geometry
are reviewed. Planner was compiler-inlined; original rejected separate-symbol
review is preserved. Patch SHAf96213a24c98b47d430ffa1f8f92ecec572131c049016b462649e06a697c7ab5.
Control binarybfca6ebfac21c24e9ddcbdfad158cba438679844af4cd3ec7f4fb1d354556a61;
candidate86381a4d3cd8d3fcb4aac17e35fc175ddc479af097efb13e87706a3c99377933.

Fresh ordinary183 control/candidate each passed50 live pixel/copy checks,
25timed loops/50scanout comparisons, guarded restart and full cold integrity.
Candidate counters prove top-down/bottom-up eligible copies and all10000 timed
DIB uploads. Complex-clip and24bit fallback observed. See183pair-review.json and
raw sample logs retained privately. Both strictFALSE only inheritedFtdisk49;
no warning/event waiver or application/popup delta. No physical access.

Upload medians0.2100ms control vs0.2175ms candidate: no demonstrated benefit.
All samples retained, including candidate first-sample timing outlier. Coarse
GetTickCount, matched accounting, background work and ordered boots prevent
attributing small timing differences to the driver. This experiment is retained
as exact-copy/coverage evidence and is NOT selected for hardware deployment.

Compiled row copy already uses libcntpr memmove with aligned REP MOVSD, not a
byte-only loop. Further work should compare genuinely different UC row-store
instruction sequences with exact bytes/geometry and matched ordinary boots;
do not claim that replacing memcpy alone fixes a byte-copy bottleneck. No SIMD,
FPU, WC, GPU or higher-mode change is justified by this pair.

Host command construction refusal and compiler-inlined-symbol review refusal
are retained. All builds and183sessions CLOSED. Physical0101/video0093,0088rollback
and immutable0.1.0 unchanged. No release or hardware performance qualification.
