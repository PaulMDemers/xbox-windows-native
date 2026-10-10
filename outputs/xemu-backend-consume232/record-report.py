"""Record closed232 evidence and prepend continuation without altering old bytes."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'REPORT.md';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');q=read(k/'consume-review001.json');b=read(k/'build001.json')
assert h['closed'] and a['cpu_scope_passed'] and a['integrity_passed'] and q['passed']
launch=read(k/'trace001/launch.json')['cycles'][0]
tests=read(k/'consume-test001.json')['runs'];pub=read(k/'publication-test001.json')['runs']
dest.write_text(f'''#232 CLOSED: bounded actual consumer preserves the real NOP wait

One fresh stopped-dashboard diagnostic followed by ONE Windows launch,
accepted {launch['launch_requested_utc']}; normal dashboard return
{launch['dashboard_return_utc']}; full controller/cold closure
{h['closed_utc']}. Preparation88498/build8773/host-tests2461/runtime18232 CLOSED.
Controller{h['controller_pid']}/runner{h['runner_pid']}/tracer{h['tracer_pid']}/
observer{h['observer_pid']} CLOSED. Never replay/recollect this case.
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
{tests[0]['stdout'].strip()}
{tests[1]['stdout'].strip()}
These include partial packets/lookahead limits, loop budgets, access refusal,
waits, errors, stale/expired request, invalid range/count and ordinary NULL
comparison. PGRAPH dispatch/DMA map/byte load/clock are explicit host adapters;
this is not GPU execution. Actual publication helper/report tests at O0/O2:
{pub[0]['stdout'].strip()}
{pub[1]['stdout'].strip()}
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
sources restored byte-exact. Compiled exe SHA256 {b['executable_sha256']}.
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
''',encoding='utf-8')
cont=ws/'outputs/engineering-notes/CONTINUATION.md';old=cont.read_bytes()
prefix=f'''# Current checkpoint: consume232 CLOSED; actual guest-dependent wait

ONE fresh opt-in actual consumer run CLOSED at {h['closed_utc']}. No physical
access/device merge/tag change. Head before this turnc866915. All root owned
sessions8773/2461/88498/18232 and PIDs114836/78228/69944/115420 CLOSED;
cooperative leases released. Never rerun/recollect closed232 trace001.

Build/test/review inputs byte-pinned; four model files changed, SIX borrowed
files restored. 32768 iteration/word budgets and5sec real-time limit, real
wait/error preservation, ordinary NULL budget. O0/O2 actual-parser ASan/UBSan
46672 checks/10000packet cases each; actual publication ~1.69M checks/100000races/
10000pairs each;72guards. Host adapters are explicit, not GPU execution.

Runtime refused state4/reason20/stop4, raw NOP wait2->2, zero iterations/words;
GET03fbe750/PUT03fcea10 unchanged backlog66240, parser count/error0.212992 actual
reserved bytes unchanged; GDB mode restored, no guest breakpoint/memory writes.
No dirty readback, reference retirement or native grant. CPU65 allocations/
releases3194880bytes and four joined workers; normal restart/dashboard; cold
320dirs6723files321clusters0errors/orphans,5hives/protected/policy passed.
StrictFALSE sole inheritedFtdisk49; GPU/ordinary/physical/native unqualified.
Existing211 wizard policy explicit, NO synthetic null device policy.

Actual pinned pgraph.c static sites set NOP wait on nonzero NV097NO_OPERATION
and clear it through guest NV_PGRAPH_INTR acknowledgement after ERROR absent.
No runtime method/parameter/interrupt/acknowledgement captured. Next NEW bounded
read-only producer/clearer/IRQ lifecycle observer before owned handoff; never
clear waits or resume producers within an accepted preservation request.
See outputs/xemu-backend-consume232/REPORT.md and WAIT-NEXT.md.

Audio reported capability note complete, audibility unknown; PCI remaining
STOP/cancel/SMBus/takeover gates continue. USB reported no-XID second-boot stale
data/12orphans4a2f1f6, unresolved; preserve failed disks. Root first-boot cold
checks DO NOT resolve repeated-boot storage. Authorized continuation/lease
release messages sent. Peer report cursors in coordination001.json.

Fresh private fixture E:/Codex-archive/xbox-windows-native/consume232/
trace001-source.qcow2; private run E:/Codex-private-artifacts/
xbox-windows-feasibility/consume232-runs/nt5-consume232-trace001. Preserve
physicalFATX0101/video0093,0088rollback,immutable0.1.0,all old evidence.
C24.45GB/E163.1GB free at22:20UTC;20GiB build guard unchanged.

--- Previous continuation retained byte-exact below ---

'''.encode()
cont.write_bytes(prefix+old)
(k/'continuation-record001.json').write_text(json.dumps(dict(old_sha256=hashlib.sha256(old).hexdigest(),prefix_bytes=len(prefix),new_sha256=sha(cont),old_tail_preserved=cont.read_bytes()[len(prefix):]==old,physical_access=False),indent=2)+'\n')
print('232 report and byte-preserved continuation recorded')
