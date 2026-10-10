# 216: context-switch prerequisite identified

Two fresh ordinary emulator runs completed the retained display workload and
normal shutdown. The read-enabled candidate captured 26 approved registers at
each of two passive hooks. Both snapshots have an invalid PGRAPH context,
PFIFO channel 1 and PGRAPH channel 0. In the exact compiled xemu model, a request
for this channel would enter the software context-switch path. The existing
miniport supplies no HwInterrupt handler to service that path. This is a
concrete prerequisite for the resident adapter, not a submission experiment or
proof that the GPU is idle.

The scoped display and cold integrity checks passed for both runs. Whole-boot
strict qualification remains FALSE: each added exactly the inherited Ftdisk 49
event for HarddiskVolume6. No gate was waived. No physical console access,
GPU writes, context initialization, IRQ acknowledgement, RAMIN/USER mapping,
mode change, cache change or device-policy change occurred.

## Actual runtime state

The candidate emitted 56 diagnostic records, including 52 reads, with no missed
records. The OFF control emitted two phase markers and performed no new reads.
Phase 0 is before the retained ready marker after mode initialization; phase 1
is the first successful shared framebuffer mapping. The observations are
sequential register reads; their equality does not establish an atomic snapshot
or quiescence.

| Observation | Phase 0 and phase 1 | Meaning in the pinned model |
| --- | --- | --- |
| PGRAPH_CTX_CONTROL | 0x10000100 | Context-valid bit 16 is clear |
| PGRAPH_CTX_USER | 0x00000001 | Context channel bits select channel 0 |
| PFIFO_CACHE1_PUSH1 | 0x00000001 | PIO channel 1 |
| PGRAPH_DEBUG_3 | 0xf3de0479 | Hardware context-switch bit 2 is clear |
| PFIFO push / pull access | Both disabled | Observed access bits, not idle proof |
| PGRAPH FIFO access | Enabled | Does not grant ownership |
| PFB_CFG0 | 0x03070103 | Stored configuration word |
| PFB_CSTATUS | 0x04000000 | The model reports 64 MiB VRAM |
| PCRTC_START | 0x03c00000 | Retained scanout address |

The model's pgraph_context_switch checks validity and channel identity. With
these observed bits, a submission requesting FIFO channel 1 needs the software
switch path and a context-switch interrupt. Hardware switching is disabled;
enabling it is not a workaround because that branch asserts unsupported in this
model. No request was submitted, so no actual context-switch interrupt, wait,
completion or drain was observed. See state-observations.json and the exact
source pins in evidence-review.json.

## Boot handoff evidence and remaining ownership gap

The fixture's launcher SHA c7a2b9c8 and FreeLoader SHA c936b06e match the
historical owned build outputs. Seventeen source files and the historical
launcher object/disassembly were captured privately. The current historical
FreeLoader source may include later edits; its content pin does not prove a
clean reconstruction of the old binary.

The inspected XBE and Cromwell paths replace the dashboard CPU interrupt
environment, stop USB, execute CLI, clear/reload the IDT and transfer control.
The 64 MiB Multiboot map reserves [0x03c00000, 0x04000000) as type 0; the current
Xbox loader source maps that type to LoaderFirmwarePermanent. The retained
loader checks scanout against this reservation. None of these inspected paths
passes an instance-memory ownership record or proves the former GPU producers
have drained. CPU interrupt shutdown cannot substitute for GPU release.

The actual indexed bootvid backbuffer occupies
[0x03fb2d00, 0x04000000), 316,160 bytes. The earlier pbkit 20 KiB overlap remains
counterfactual because NV2A's physical instance backing has not been established.
Linux's NV04-family implementation reserves 512 KiB at the end of VRAM for
PRAMIN, and envytools describes related PRAMIN write protection. These are
bounded research leads, not an NV2A address contract. The exact captured content
hashes and URLs are in references.json. Sources:
[Linux v6.12 allocator](https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv04.c)
and [envytools PFB description](https://raw.githubusercontent.com/envytools/envytools/master/rnndb/memory/nv10_pfb.xml).
The envytools capture is content-hash pinned, not a claimed immutable revision.
xemu's separate 1 MiB RAMIN storage cannot validate a physical UMA alias.

## Validation and closure

| Case | Accepted UTC, 2026-10-10 | Dashboard return UTC | Closure UTC |
| --- | --- | --- | --- |
| control001 | 02:26:29 | 02:30:42 | 02:31:01 |
| candidate001 | 02:32:13 | 02:35:54 | 02:36:13 |

Each unique child passed five display samples, 200 window moves with exact
readbacks, 65 text cases and matching upload phase totals. The retained mode is
1024x576x32 at 60 Hz. Each cold allocation scan covered 325 directories,
6,730 files and 326 directory clusters with zero errors/orphans. Five structural
hive checks, protected hashes, startup, typed device state and normal shutdown
passed. Application and measurement event deltas are clean; the sole whole-boot
error is Ftdisk 49. This is not a performance comparison.

The native OFF/ON miniport hashes are respectively
46dfc7f649a3bba04b8e6d23150e6591a074249eef4514a096f291e2edbb1736 and
7dc3dbb77faa60f9dda634275e972169b27e12203c95ba1cdf00261d2920dd25.
The shared main object is identical; the actual NT5 read-provider import and
its body were checked. Host ASan/UBSan checks passed: 109 OFF, 400 ON, including
32 joined concurrent callers and rejected malformed calls. Parser mutations
passed 294 checks; the independent context decoder passed 4,096 truth-table
cases. These are host tests, separate from ordinary guest evidence.

The final evidence review checked 127 source, binary, fixture, trace and cleanup
pins. Both runner/observer/controller groups are closed. Never relaunch or
recollect these cases. Private artifacts remain in the E: gstate216 fixtures
and runs; provenance and reports are tracked, binaries are not.

Prelaunch harness failures are preserved: inherited inventory cardinality and
object-path mistakes, and initial adapter newline normalization. Distinct 002
captures and byte restoration fixed them before freezing 49 launch inputs.
The first post-run pair comparison was invoked with Windows Python instead of
the required WSL environment and failed at import, before creating output.
The dependent closure review consequently had no pair report. The unchanged
comparison then passed under WSL, followed by the unchanged closure review;
there was no guest relaunch or cold recollection.

C: briefly fell below the unchanged 20 GiB guard during control. The closed
standalone hardware-probe-005 was copied and hash/readback verified on E:,
with its original path retained through a junction. The manifest is
outputs/task-storage-offload/manifest-hardware005-20261010.json. No backing
chain was moved. C: had 22,267,056,128 bytes free at closure review.

Physical FATX0101/video0093, original0088 rollback, immutable0.1.0 and all failed
evidence are unchanged. Instance backing/reservation, exclusive context
acquisition, native submission and genuine completion/drain remain required.
