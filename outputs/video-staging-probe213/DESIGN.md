# Native buffer precursor213

This isolated miniport probe exercises the actual NT5 allocation and release ABI
before any GPU programming. Only XWN_STAGING_PROBE differs between matched
OFF/ON helper builds. The common miniport object is byte-identical. HAL/FATX,
shared0106 bootvid, accounting119 display and captured physical-core policy remain
unchanged. This is an emulator precursor, not a deployment candidate.

ON records passive IRQL, allocates16KiB with MmNonCached within0x100000..03bfffff,
checks four page translations plus the last byte, initializes source/destination/
staging and guards, and copies a58x13 rectangle through four bounded strips.
Different pitches256/272 expose row-offset errors. Independent expected bytes
include destination padding, untouched pixels, all source bytes and allocation
guards. Successful trace21302 reports15,365 checks/four strips/no failure;
21303 occurs after the matching free returns. No address reaches a DMA engine.

OFF records its mode and returns. Normal framebuffer initialization then proceeds
in both cases. ON verification failure returns FALSE rather than manufacturing
success. Since no GPU operation exists, post-allocation failures can free the
buffer. That cleanup is explicitly unsuitable for an in-flight DMA timeout.

Host003 uses the exact native helper with injected wrong IRQL, allocation failure,
misalignment, inconsistent page/last-byte translations, corrupted destination,
source and guard bytes.27 OFF/96 ON checks pass with ASan/UBSan, including the
matching free on every failure after allocation. Host001/002 preserve a harness
expectation error: thirteen rows cause26 copy calls, not8 calls per four strips.
The production helper did not change to obtain that correction.

build001 preserved the attempt to reuse210 object files that had never been built
for that target. build002 compiled OFF but ON linking exposed a thin CRT archive
with uncopied relative members. build003 uses the existing fully compiled106
miniport target, pins its source/headers/unchanged objects/import libraries, and
copies/indexes every thin archive member into a regular private archive. This
small build preserves the20GiB guard and does not edit or rebuild old fixtures.
It is not represented as a complete source reconstruction.

build-review.json checks actual intended fixture providers. review001-failure
preserves selection of the original physical bootvid, which has no XwnFb exports;
the fresh emulator fixture actually uses shared0106. Corrected review002 pins
that exact provider instead. No physical bootvid was replaced in this session.
Both helpers are in a nondiscardable .text section; on-disk bytes are not a claim
of runtime residency. ON adds exactly the three reviewed memory imports.

Each fresh child runs the retained211 five-sample GDI workload with accounting
ON in both; only the miniport probe differs. The immutable211 prelaunch parent
stays unchanged. Helpers use new xwnst213a/b directories; startup paths change
only in those children. Inherited targeted wizard cancellation remains explicit;
no null device, disabled service or error gate is introduced. Require exact new
probe trace, retained pixel/coherence/counter/phase scope, one normal shutdown,
dashboard return, full cold allocation/hive/protected-file and typed-policy audit.
Whole-boot Ftdisk49 remains a strict failure if observed.

All GPU initialization, DMA submit, scanout/cache conversion, mode changes,
timing/speed claims and physical qualification remain out of scope. A buffer
precursor PASS cannot waive queue/context/instance-memory/drain/crash contracts.

Closed control001 returned normally, but its first host auditor stopped during
imports: boundary_analysis.py had not been copied with runner_analysis.py. No
cold reader opened. The original frozen auditor/controller failure is preserved.
The exact unchanged211 dependency was added; audit-emulator002 adds its hash
guard and performs the first actual cold audit of that preserved disk. There was
no second guest launch or repeated allocation scan. Candidate001 then used the
original frozen auditor with that dependency present and closed successfully.
Both strict results remain FALSE for the sole inherited Ftdisk49 event.

Build003's leading description inherited a210 donor label; its recorded commands
and paths identify the fully compiled106 object/import-library donor. Exact source
and dependency hashes, the single helper-call overlay and identical common object
are checked in native-input-review.json. This label is not full-build provenance.
The post-run pair comparison imports WSL cold utilities through common.py and
must run in WSL. A first Windows invocation stopped at imports before producing
the pair report; the subsequent WSL invocation was read-only and passed.
