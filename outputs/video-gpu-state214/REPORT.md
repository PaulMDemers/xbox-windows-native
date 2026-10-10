# Read-only GPU state214

The matched ordinary emulator pair passed the observational snapshot, retained
GDI and cold integrity scopes. Candidate001 performed exactly44 new register
reads:22 after retained-mode initialization and22 after the first successful
shared framebuffer mapping. Both snapshots were identical. This establishes a
bounded read path in the actual NT5 miniport; it does not accelerate drawing or
establish GPU ownership, idle state, completion or physical operation.

Control001 was accepted2026-10-10 01:35:20 UTC and closed01:39:42. Candidate001
was accepted01:41:04 and closed01:44:54. Each had one launch, normal shutdown and
dashboard return, followed by one full cold audit. Both cases are CLOSED and
must never be relaunched or recollected. All root-owned214 processes are closed.

The actual register observations include:

| Register | Both snapshots | Interpretation limited to pinned model bits |
|---|---|---|
| PMC_BOOT_0 | 02a000a3 | Expected emulator chip word |
| PMC_INTR_0 / INTR_EN_0 | 01000000 / 00000001 | Pending and enable words retained |
| PFIFO_RAMHT / RAMFC / RAMRO | 03000100 / 00890110 / 00000000 | Configured table words; allocation ownership unproved |
| CACHE1_PUSH0 / PUSH1 | 00000000 / 00000001 | Push access disabled; channel1, PIO mode |
| CACHE1_DMA_PUSH / STATE | 00000000 / 00000000 | DMA push access disabled; status bit12 clear |
| CACHE1_DMA_PUT / GET / PULL0 | 00000000 / 00000000 / 00000000 | Equal pointers; pull access disabled |
| PGRAPH_INTR / INTR_EN | 00000000 / ffffffff | Raw interrupt words |
| PGRAPH_CTX_USER / FIFO | 00000001 / 00000001 | Context channel0; FIFO access enabled |
| PCRTC_INTR_0 / INTR_EN_0 / START | 00000001 / 00000001 / 03c00000 | Retained scanout and interrupt words |

PFIFO channel1 and PGRAPH channel0 are distinct observed fields. No conclusion
about whether a channel is free follows. Disabled push/pull access, equal
pointers and stable values do not prove engine idle or exclusive ownership.
PCRTC raster and PGRAPH indexed-data reads were excluded because the actual
compiled xemu handlers mutate state. RAMIN was not read. No PGRAPH_STATUS symbol
or unimplemented PMC_ENABLE capability was invented. Complete raw values and
declared bit masks are in state-observations.json and model-inventory.json.

Each child retained five GDI samples,200 movement/readback steps,65 text cases
and exact119 upload phase coverage. Pixel results, scope and upload phase byte
totals matched. Full cold allocation in each:325 directories,6730 files,326
directory clusters,zero errors or orphans. Five structural hives, protected
files, startup history and typed device policy checks passed. There were no
measurement-interval or application events. Trace missed count was0; OFF emitted
two markers and ON emitted48 records for its44 reads. Exact trace hashes are
recorded in the per-case audit.json files.

Whole-boot strict qualification remains FALSE in both for the actual inherited
Ftdisk49 on HarddiskVolume6. That event is retained, not waived or suppressed.
These display and integrity passes do not qualify complete storage/dump recovery,
new video modes, performance, GPU transfer, a release or physical deployment.

The fresh matched native builds share the exact same common miniport object.
OFF SHA25639bf01a849152f0b175685b32c00d0af2480ad05df7edda59b060d111ce8f981;
ON23b76c42017206cd6df45c32249c58205556a2c18d897d98b9ceaa9d01e861b2.
The208/384-byte helpers reside in nondiscardable.text. ON adds exactly one import,
ntoskrnl.exe!READ_REGISTER_ULONG. Its pinned actual NT5 provider is pointer load,
register load,ret4; modern barrier implementation details are not imputed to it.
This is a small pinned target build using the106 object/import-library donor and
210-compatible source, not a complete clean source reconstruction. Native input
review passed240 pins; closed evidence review passed341 pins. The45 frozen
prelaunch source/binary/fixture identities remain unchanged.

Host002 passed105 OFF/352 ON ASan/UBSan checks with five invalid contexts,
duplicate phases and32 joined concurrent callers. Host001's sanitizer success
remains preserved beside a later source-review failure: its test check counter
was not atomic. Only the host harness changed for002; production source and
native binaries did not change. Its exact executed-script provenance is retained.
Parser002 passed254 checks. The original parser harness wrongly expected an
additional unrelated legacy record to fail the214 family scope; that failed
oracle remains preserved. The parser itself did not change. Its corrected tests
retain the maximum count bound and exact214 lifecycle requirements.

The fixture uses the immutable211 prelaunch parent, retained accounting119 ON,
HAL/FATX/shared0106 bootvid and captured physical-core device policy. The targeted
wizard Cancel helper remains explicit; unknown dialogs hold the run. No synthetic
null device, service suppression, device disable, GPU/model write, cache change,
new mapping or reset was introduced. xemu's separate RAMIN backing remains a
physical qualification gap. No physical access occurred. FATX0101/video0093,
original0088 rollback and immutable0.1.0 remain unchanged.

The next step is a concrete resident addressing/context/completion contract,
grounded in these retained registers and the exact model/source paths. See
NEXT.md. The eventual first transfer must use disjoint guarded storage and a
CPU oracle, with bounded failure/drain/quarantine behavior before scanout use.
