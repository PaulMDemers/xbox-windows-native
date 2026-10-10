#225: executing loader handoff preserves inherited GPU objects

One new emulator debugger child CLOSED, handoff/CPU/integrity scope PASS.
Exact executing-code pins and532480 raw memory bytes independently verified.
No native binary changes, GPU writes/grants, physical access or device merges.
Strict whole-boot result FALSE: the sole inherited Ftdisk49/error3 remains.
This diagnostic is not ordinary or physical qualification or acceleration.

## Actual executable relationship

The294384-byte XBE has the exact282076-byte Cromwell payload at file offset
0x3000. All three linked ELF load sections match that payload byte for byte;
this establishes useful linked instruction addresses without asserting a clean
historical source rebuild. Nine original216 Cromwell source pins match current
files; other source is a bounded consumer lead. The first inventory accidentally
decoded embedded data after an unsized terminal thunk. Original evidence and
correction are retained; only sized-function inventory002 is authoritative.

Runtime pins64 actual bytes at each of these executing addresses:

| Boundary | Address | Observed CPU state |
|---|---|---|
| startReactOS.part.0 entry |03a0c4e0|interrupts enabled|
| BootStopUSB returned |03a0c506|interrupts enabled|
| CLI executed |03a0c530|interrupts disabled|
| final multiboot RET |03a0c6d8|interrupts disabled|
| actual FreeLdr entry |00200a20|interrupts disabled|

Exact169984-byte FreeLdr is verified in the uploaded buffer and after copying to
00200000. The final RET targets00200a20 with EAX2badb002 and the same EBX info
pointer at FreeLdr entry. Actual descriptors reserve03c00000..04000000 as video
memory. The existing launcher's entry-size/count convention is recorded exactly.
CPU paging is off throughout; no debugger memory/register write was performed.
The frozen design's USB "paired instruction return" means the instruction after
the statically pinned call, not a separate runtime entry/return-frame pair.
Five one-shot breakpoints removed, remaining count zero, guest resumed normally.

## GPU state crosses the boundary unchanged

Each stop captures26 approved register reads,20KiB RAMIN and the84KiB reserved
CPU video tail. All26 registers and both complete raw regions are identical at
all five stops. Independent review verifies130 register observations and532480
memory bytes. xemu RAMIN and CPU tail are separate captures and different backing
stores; their preservation is not a physical UMA alias/ownership proof.

The same inherited state survives USB removal, CPU interrupt revocation and the
loader transfer: PFIFO channel1, PGRAPH channel0, current graphics context invalid,
hardware context switching disabled. RAMHT base10000/size4096 is fully captured;
22 valid entries remain, all assigned channel0. Their captured descriptors include
graphics classes0097,009f and0062 used by the proposed215 protocol, but these are
existing firmware objects, not a new NT5 grant. RAMFC/RAMRO raw settings and the
remaining indirect source paths are retained without inventing an allocation map.

This shows actual CPU shutdown does not invalidate the inherited object table;
no explicit GPU ownership record was found in the examined handoff. Unchanged
bytes alone do not prove or disprove a transfer by some other convention. The
trace does not prove backend idle or identify
every firmware reference. Quiet DMA pointers/interrupts and model constant empty
status remain insufficient for retirement. No reset, borrowed channel, context
request, descriptor store or completion/drain claim was made.

## Normal workload and cold checks

Fresh standalone seed: private E:/Codex-archive/xbox-windows-native/handoff225/
trace001-source.qcow2. Parent is immutable211; full virtual comparison identical,
parent unchanged, no backing dependency in seed. Private closed run:
E:/Codex-private-artifacts/xbox-windows-feasibility/handoff225-runs/
nt5-handoff225-trace001.136 frozen inputs remain exact.

Unchanged224 candidate driver/probe retains its compiled xwnret224 namespace,
candidate219 bootvid and exact211 wizard cancellation. Inherited null policy is
FALSE; selected device/storage/video policies unchanged. Native helper records
128 additional GPU reads and refuses exposure. CPU cleanup completed65 actual
allocations/releases/refusals,3194880 verified bytes, four joined workers.
One normal EventLog6006 and dashboard return; no application events/popups.
Cold allocation320directories/6724files/321directory clusters,0errors/orphans;
five structural hives,28 protected hashes, startup and event/SetupAPI histories
pass. This does not qualify every file's payload or native fallback fault paths.

Accepted2026-10-10T18:31:18.099143UTC; returned18:32:40.281556;
closed18:32:59.315779. Controller103104, runner111336, tracer108876,
observer100732 and preparation/session95713 are CLOSED. Runtime session49767
CLOSED0. No old launch, collection or audit was repeated.

C: fell below20GiB during the active guest. No new build was started. Two CLOSED
historical standalone probe directories were copied to E, all68 files hash-
verified, original paths preserved with verified junctions, originals removed
only after containment/readback checks. Approximately1.912GB preserved/offloaded;
manifest is outputs/task-storage-offload/manifest-handoff225-20261010.json.
No QCOW backing chain was moved and the20GiB guard remains unchanged.

## Next

Use actual preserved RAMHT/descriptor bounds to specify the reserved old-owner
ranges and a new serialized NT5 ownership transition. Establish bounded backend
drain/completion and software context service before any16x8 submission. An
explicit release record must account for inherited channel0 objects; neither a
CPU-off witness nor copied firmware handles may grant reuse. No further quiet
register repetition is needed. Runtime PTE/cache alias coherence and native
cleanup fallback fault paths remain distinct work. Keep0101/video0093 physical
baseline,0088 rollback, immutable0.1.0 and all failed evidence unchanged.

Evidence: inventory002.json, inventory-correction.json, evidence-review.json,
trace001/trace.json, audit.json, host-state.json, launch.json and closure.json.
