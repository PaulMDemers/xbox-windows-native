# Exact0101 directory-query source lead; runtime confirmation pending

Read-only source001 captures five files BYTE-IDENTICAL to recorded build tree
8e12297ca0ed53383fe9aaebef152c26aee5a43b; build-report associates this with installed
FATX SHA ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9.

FindFile in create.c adjusts cached startIndex by2 for nonroot FATX when comparing
against the enumeration cursor. Its successful cached result returns raw
rcFcb->dirIndex and raw rcFcb->startIndex. In contrast FATXGetNextDirEntry's slow
path presents synthetic dot/dotdot positions then real slots with+2 indices;
vfatMakeFCBFromDirEntry subtracts2 when storing the nonroot FATX indices.
DoQuery in dir.c advances the caller cursor to returned DirIndex+1.

Hypothesis: a resident exact-name FCB returns a cursor behind its logical slot;
subsequent queries can return that same entry repeatedly. This would explain
385 CMD MOVE reporting multiple files for one source.387 actual FindFirst/Next
will determine whether this behavior is present; do not claim source inspection
alone establishes the hardware producer. No driver patch/build/deployment yet.
All existing physical drivers and rollback files remain unchanged.

Host001 extracted exact original cached-FCB branch reproduces repeated returned
index. Proposed host-only normalization of both returned indices by2 for nonroot
FATX passes708 checks across root/nonroot/FAT controls and boundary indices, with
267 balanced modeled release/cleanup calls, ASan/UBSan clean. Strings and release/
cleanup helpers are explicitly modeled; no driver built, installed or runtime PASS.
387 did not execute its probe. Independent emulator389 preparation is next.
