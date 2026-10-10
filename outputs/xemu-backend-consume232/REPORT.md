#232 CLOSED: bounded actual consumer preserves the real NOP wait

One fresh stopped-dashboard diagnostic followed by ONE Windows launch,
accepted 2026-10-10T22:18:10.759240+00:00; normal dashboard return
2026-10-10T22:19:32.591205+00:00; full controller/cold closure
2026-10-10T22:19:53.529988+00:00. Preparation88498/build8773/host-tests2461/runtime18232 CLOSED.
Controller114836/runner78228/tracer69944/
observer115420 CLOSED. Never replay/recollect this case.
No physical access, device integration or release tag change.

The new opt-in model calls the ACTUAL existing PFIFO parser/PGRAPH puller with
32768 iteration/committed-word limits and the inherited five-second real-time
deadline. Jump-only loops consume the iteration budget. Method lookahead is
capped to the remaining word budget, including original cross-packet lookahead.
Ordinary worker calls pass NULL, retaining existing assertions/parser and lock
transitions. Waits/errors are not cleared, GET is not synthesized and producers
remain paused through the owned request. Invalid ranges/counts/errors and host
uncertainty quarantine. Actual backend writes to either sampled reserved range
also quarantine until attributed. GL calls are not all cancellable; the owned
host watchdog remains separate. 231 release/acquire terminal publication and
timeout tuple withholding cover the new telemetry too. No generalized native
producer-ownership or GPU visibility contract is claimed.

Actual compiled parser/masks/QEMU atomic headers passed explicit host-adapter
tests at O0/O2 with ASan/UBSan:
checks=46672 packet_cases=10000 ordinary_comparisons=covered jump_budgets=covered native_grants=0
checks=46672 packet_cases=10000 ordinary_comparisons=covered jump_budgets=covered native_grants=0
These include partial packets/lookahead limits, loop budgets, access refusal,
waits, errors, stale/expired request, invalid range/count and ordinary NULL
comparison. PGRAPH dispatch/DMA map/byte load/clock are explicit host adapters;
this is not GPU execution. Actual publication helper/report tests at O0/O2:
checks=1693953 concurrent_pairs=100000 publication_pairs=10000 completed=89611 timed_out=10389 native_grants=0
checks=1692287 concurrent_pairs=100000 publication_pairs=10000 completed=89849 timed_out=10151 native_grants=0
Both sanitizer runs clean; 72 actual-helper guard checks and PowerShell syntax
passed. No compiled/test guest failure was discarded or replayed this turn.

Runtime state4/refused, reason20 =16+consume_stop4; tuple_published1/version232.
Raw waits before2/after2 identify waiting_for_nop, with zero iterations and
zero committed words. GET03fbe750/PUT03fcea10 and DMA_STATE00000104 are unchanged:
numerical backlog66240bytes, parser count0/error0. STATUS00000010 remains
unchanged. No method reached the puller. Surfaces/dirty/downloaded/bytes all0,
references_retired0/native_grant0. Thus this run validates safe refusal and
telemetry; it does not validate an actual consuming guest drain or readback.

GDB physical mode query/set/query and restore/query succeeded. 212992 actual
before/after bytes prove old20KiB RAMIN and84KiB CPU tail unchanged during this
diagnostic. No guest breakpoint/register/memory writes. Actual guest resumed
only after terminal refusal and safe mode restoration; no forced empty state.
consume-review001.json independently verifies the raw snapshots and masks.
Byte-pinned compiled pgraph.c identifies the static nonzero NO_OPERATION wait
producer and guest NV_PGRAPH_INTR clearer. Runtime did NOT capture that method,
parameter/interrupt or guest acknowledgement. See wait-source001.json and
WAIT-NEXT.md; never treat those static leads as a recorded full lifecycle.

Unchanged224 CPU manager passed65 allocations/releases,3194880 verified bytes,
65 exposure refusals/four joined workers. Eight rounds/128 MMIO reads retained
UNMODELED_BUSY/NO_OWNERSHIP refusal. Explicit inherited211 wizard policy made3
actions/idle, no synthetic null devices. Normal6006 count1/dashboard return,
no application event delta. Full cold allocation320dirs/6723files/321dirclusters,
0 errors/orphans. Five structural hives/protected hashes/startup/history/device
policy checks passed. Selected payload/hive integrity is not all-file-content
or repeated-boot storage qualification. Sole inherited Ftdisk49/error3 remains
strict failure. Strict/GPU/ordinary/physical/native qualification remainFALSE.

Source revision e72e76bd1f12ce45c6c63b4196c6918ea2cc705d and pinned toolchain
unchanged. Four files changed: nv2a.c/int.h, pfifo.c, GL renderer.c. GL surface
predicates and actual QEMU atomic/compiler headers unchanged. All SIX borrowed
sources restored byte-exact. Compiled exe SHA256 de062835f6aa0b79b25c77eb1ce169e5b9a441721bce9c8856b4ed4597c6f7af.
Full source pins candidate001-source-pins.json. Fresh private fixture
E:/Codex-archive/xbox-windows-native/consume232/trace001-source.qcow2; run
E:/Codex-private-artifacts/xbox-windows-feasibility/consume232-runs/
nt5-consume232-trace001. Private binary/disks/raw reads/hives remain excluded.

Device chat check: audio capability note/source manifest complete, audibility
unknown; PCI STOP/cancel/functional SMBus/terminal takeover open and audio
installation blocks normal restart. USB reported no-XID second-boot stale data
and12orphans at4a2f1f6; cause unresolved. Authorized independent investigations
continued after root cleanup/lease release; no candidate merged. These are
peer-reported results, distinct from root's single first-boot/restart audit.

Next NEW bounded diagnostic observes actual NOP producer/guest IRQ acknowledgement
before a separately owned stopped-CPU handoff. Preserve waits/refusals and end
references independently. Preserve physical0101/video0093,0088rollback and
immutable0.1.0. No owned root processes remain. See WAIT-NEXT.md.
