# Boot layout219: matched display scope passes; live tail guards pending

The isolated candidate protects the top 84 KiB of the permanent four MiB boot-video
mapping and moves indexed backing below it. ResetDisplay now clears only the
bounded writable domain. Shared allocation/cache policy/ABI and GPU behavior are
unchanged. Physical0101/video0093, original0088 and immutable0.1.0 are preserved.

Host actual-body ASan/UBSan tests pass 131173 control and 16547909 candidate checks
across two modeled RAM profiles, four geometries and both reset modes. Candidate
retains tail and outer sentinels through reset, fills, text, saved-row restore,
scrolling, palette redraw and packed bitmap readback. Control confirms the old
whole-mapping clear destroys tail sentinels. These are host tests with modeled
HAL/font/palette wrappers, not actual kernel initialization or crash guards.

Fresh matched bootvid builds compile with unchanged import/export names and
actual NT5 kernel/HAL export compatibility. Candidate DLL SHA256:
50c3487e68efcfd6e6bc0718f4e172776a54f6b8eb68ee565868c2825a3e3576.
Native review verifies 95 dependency/child/input pins; runtime freezes 56 inputs.
This recompiles both bootvid translation units using pinned reused supporting
objects/resources/import archives, not a full clean native source reconstruction.
Both prepared standalone children have 320 directories, 6719 files, 321 directory
clusters, no allocation errors/orphans and five parsed hives. Parent unchanged.

Both ordinary runs are CLOSED. Control launched 04:49:43Z and returned 04:53:55Z;
candidate launched 04:55:02Z and returned 04:58:46Z on October 10, 2026. Each
completed five GDI samples with copy, pixel, window, text and upload checks,
setup-idle and joined helper gates, normal shutdown count 1 and observed dashboard
return. Independent post-closure review verifies every 159-transition upload
sequence in all five samples each. Both keep 1024x576, 32bpp, 60Hz and equal caps.
No emulator timing qualifies physical speed or additional modes.

Each full cold allocation has 325 directories, 6730 files, 326 directory clusters,
zero errors/orphans; five hives parse and 28 protected files match. Startup and
device policy remain unchanged; inherited_null_policy is false. The only new
warning/error is identical Ftdisk49 HarddiskVolume6 error3 outside measurement,
with no application events. Display scope passes; strict overall qualification
remains FALSE on both sides. No event gate was waived. Metadata/hive/protected
checks do not constitute an exhaustive all-file-content audit.

Initial read-only observer fails: the historical fixed 823df000 kernel address
is inaccessible. Its bounded result remains independent from ordinary scope.
Separate observer002 discovers candidate kernel 82403000 using two IDT gates,
pins its PE and loaded bootvid's 64 relocated reset bytes, and reads globals twice:
FrameBufferStart FCED7000, BackBuffer FD274D00, HiddenOffset 39dd00 and
BootWritableBytes 3eb000. Observer003 independently reads all 1024 PTEs twice in
bounded groups, confirming the original 03c00000..04000000 physical reservation
and present/PCD bits; indexed backing begins 03f9dd00. Neither observer stops or
mutates the guest. Raw page bits do not establish effective PAT/MTRR types,
GPU aliases, coherent whole-map snapshots or runtime tail preservation.

Compiled reset review verifies the control's immediate 400000 clear and the
candidate's load from BootWritableBytes into memset's count. pair-review.json
verifies 67 pins, actual closures, matched payloads/policy, all full sample
sequences and read-only layout/pages. Its PASS reviews only that stated scope;
strict overall remains FALSE.

Retained failures: host001 lacked clang, with no compilation/run. Fresh002 uses
recorded gcc. First Windows-CRLF diff failed git apply --check against LF donor;
canonical002 passes and records exact LF-to-CRLF compiled source reconstruction.
Original scripts/results are preserved. Neither failure led to a guest launch.

Actual reset/crash tail guards remain pending. No GPU submission/cache handoff,
performance gain, hardware driver deployment or release promotion is claimed.
All owned sessions CLOSED: 16346, 12572, 19199, 18972; mapping observer003 closed0.
Keep cold children/parent at their original E paths. No physical access occurred
in219; original218 physical query evidence remains separate.
