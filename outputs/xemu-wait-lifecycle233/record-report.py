"""Preserve the failed233 protocol and exact partial runtime journal."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'REPORT.md';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');t=read(k/'trace001/trace.json');q=read(k/'wait-review002.json');b=read(k/'build002.json')
assert h['closed'] and a['integrity_passed'] and not a['windows_launch_record_exists']
assert not q['complete_observation_protocol'] and len(q['complete_captured_lifecycles'])==51
view=q['views']['wait_live_first'];tests=read(k/'test002.json')['runs']
busy=[v for v in t['monitor'] if 'xwn-wait233-report' in v['command'] and 'busy=1' in v['reply']]
assert len(busy)==20 and all('lock=2' in v['reply'] for v in busy)
dest.write_text(f'''#233 CLOSED: actual NOP acknowledgement observed; snapshot protocol FAILED

One fresh owned dashboard-only emulator run closed {h['closed_utc']}.
Build53097/build00265458/preparation56819/runtime44536 CLOSED. Controller
{h['controller_pid']}/runner{h['runner_pid']}/tracer{h['tracer_pid']}/observer
{h['observer_pid']} CLOSED. Never relaunch/recollect trace001. No physical
access, device integration or release tag change. All private evidence retained.

New compiled read-only observer records256 resident rows under existing PGRAPH
lock. No additional lock acquired by record/fill helpers. Producer dispatched
with FIFO released: its FIFO fields are zero and explicitly invalid. Guest
INTR acknowledgement/reset hold both existing locks and capture actual FIFO
words. Getter try-locks FIFO then PGRAPH under BQL; contention releases acquired
locks and returns busy instead of blocking. Recording does not clear interrupts/
waits, synthesize FIFO progress, disable devices or grant native GPU ownership.
Parser, GL surface/publication operations and ordinary PGRAPH/reset operations
are unchanged after removing observer insertions, independently source-reviewed.

First live snapshot succeeded: total{view['header']['total']}, retained256,
overwritten{view['header']['overwritten']}. Captured51 producer1->2 pairs,
51 guest INTR4->5 clearing pairs and51 complete captured producer/ack lifecycles.
All nonzero parameters7a080101, trapped address00000100, NSOURCE1; actual
ERROR interrupt00100000 was set with NOP wait and guest acknowledgement value
00100000 removed it. Wait2 clears only in actual acknowledgement path. These
are compiled runtime records, not just static source leads. Current first-read
NOP wait is clear; this is not producer shutdown or ownership. Producer rows'
FIFO fields remain unavailable. 51 post-IRQ-update worker-return records are
distinct from the guest acknowledgement. Leading old acknowledgement is outside
the bounded ring's matching producer coverage; overwritten prefix is unknown.
No reset pair remains in this captured window, NOT proof that no reset occurred.
Clock fields are QEMU REALTIME monotonic nanoseconds, not UTC. Guest PC and
interrupt-handler instruction identity were not captured or inferred.

The second fixed live observation FAILED:20 read-only requests reported lock2
PGRAPH busy and reached the one-second bound. The planned CPU stop, preservation
request and Windows launch never occurred. Observer rejected the unsafe phase;
the owned runner closed through its capture-complete signal. Tracer0/runner0/
audit0, observer exit1. This is failed observer protocol with valid partial
evidence; no consuming guest drain, dirty readback, terminal preservation,
ordinary/Windows/physical/native qualification. No longer retry or forced wait
clear was used. No deadlock producer identified: report bounded contention only.
Frozen original four-view decoder was never invoked on incomplete fields; NEW
decode-wait002.py decodes only actually recorded views and leaves protocol false.

Cold full allocation320directories/6719files/321directory clusters,0 errors/
orphans. Five structural hives, selected protected hashes/startup/history and
typed device-policy checks passed. No Windows launch/workload, normal6006 count0,
no new system/application events. CPU, observation and strict scope remainFALSE;
an unchanged event log from an unlaunched workload does not qualify Windows.
Selected cold integrity does not establish all-file-content/repeated-boot safety.
Inherited211 wizard policy explicit, no synthetic null-device changes.

Documentation correction:232 raw allocation files=6724, despite its report
summary saying6723. That summary subtracted the root-inclusive directory count
from child entries. Raw records/gates remain unchanged; see
allocation-count-correction001.json. No old case was replayed.

Preliminary build001 compiled but its host mask test001 FAILED: unrelated FIFO
bit2 was mistaken for access. No guest launched that binary. Both files/manifest/
test failure retained. Corrected build002 uses exact NV_PGRAPH_FIFO_ACCESS mask
and scopes new prototypes inside header guard. Actual row/fill/ring host tests,
O0/O2 ASan/UBSan each:
{tests[0]['stdout'].strip()}
{tests[1]['stdout'].strip()}
Tests use actual QEMU atomic headers with explicit clock/register/FIFO and caller
pthread-lock adapters; no actual GPU or QEMU scheduling qualification.72 guard
checks and PowerShell syntax passed. Review001 regex consumed a preceding blank
line; source diff proved that helper's mistake. Failed review source/record kept,
NEW review002 horizontal-whitespace stripper verified ordinary source unchanged.

Actual selected exe SHA256 {b['executable_sha256']}; candidate002-source-pins.json
pins full actual source. Three changed files nv2a.c/nv2a_int.h/pgraph.c over232;
all SEVEN borrowed sources restored byte-exact after both builds. Same pinned
revision/toolchain. Fresh private fixture E:/Codex-archive/xbox-windows-native/
wait233/trace001-source.qcow2; run E:/Codex-private-artifacts/
xbox-windows-feasibility/wait233-runs/nt5-wait233-trace001. Frozen inputs unchanged.

Peer-reported device progress: PCI genuine CANCEL_REMOVE/veto/handle recovery
passed at e27af87; normal restart still blocked by audio setup and STOP/CANCEL_STOP,
functional reads/takeover open. USB32f8217 reproduced stale sectors without XID:
correct file-data request addresses but seven old sectors persisted as metadata
changed. Submitted buffer/completion cause remains unresolved. Authorized
continuations and root closure/lease release messages sent. Root dashboard-only
cold checks do not resolve those peer failures. Physical0101/video0093,0088rollback
and immutable0.1.0 preserved; no owned root process remains.

Next NEW bounded worker-published immutable journal removes monitor's direct
lock dependency without bypassing real waits. See SNAPSHOT-NEXT.md. Independently
ended producers/references and actual preserving dirty readback remain separate.
''',encoding='utf-8')
cont=ws/'outputs/engineering-notes/CONTINUATION.md';old=cont.read_bytes()
prefix=f'''# Current: wait233 CLOSED partial journal; observer protocol FAILED

Head before this turn7cf4188. One dashboard-only run CLOSED {h['closed_utc']}.
All root sessions53097/65458/56819/44536 and PIDs115256/114788/113876/111276 CLOSED,
cooperative leases released. Never rerun/recollect closed233 trace001. No
physical access/device merge/release tag change. Exact frozen sources unchanged.

Actual compiled read-only256-row ring recorded total16682/overwritten16426.
51 nonzero NV097NO_OPERATION producer pairs and51 guest INTR acknowledgements
cleared ERROR00100000 and NOP wait; parameter7a080101/trapped100/NSOURCE1. No guest
PC/instruction pin. Producer FIFO snapshots invalid under PG-only lock; guest
ack rows dual-lock valid. First current NOP clear is NOT producer shutdown.
Second fixed live sample FAILED after20 lock2-busy reads/1sec bound. No CPU stop,
preservation request or Windows launch. Runner owned closure; observer exit1;
tracer/runner/audit0. Partial decoder002 PASS, full observation protocolFALSE.
No forced state clear, longer retry, native grant or dirty readback.

Cold320dirs6719files321clusters0errors/orphans,5hives/protected/startup/history/
device policy passed. No workload/normal6006(0)/new events. CPU/strict scopeFALSE,
not Windows or repeated-boot storage qualification. Inherited211 wizard policy
explicit, NO synthetic null devices. Preserve physical0101/video0093,0088rollback,
immutable0.1.0 and all failed evidence.

Build001 mask host testFAILED retained, never guest-launched. Corrected build002
actual ring O0/O2 ASan/UBSan1395checks/100000records each, wrap/saturation/read-only;
72guards/PSsyntax. Prelaunch001 whitespace-helper failure retained; NEW002 actual
source strip checks passed. Three observer files changed, seven borrowed sources
restored. Actual parser/GL/publication unchanged from232. Selected exe SHA
{b['executable_sha256']}.

Read outputs/xemu-wait-lifecycle233/REPORT.md, wait-review002.json and
SNAPSHOT-NEXT.md. Next NEW worker-published immutable bounded journal with
ordered terminal/timeout handling; do not bypass locks or assume guest owner
close. All retired-reference, dirty-readback/allocator/context/alias gates open.

Private fixture E:/Codex-archive/xbox-windows-native/wait233/trace001-source.qcow2;
private run E:/Codex-private-artifacts/xbox-windows-feasibility/wait233-runs/
nt5-wait233-trace001. No processes running. Maintain20GiB build guard.

PCI peer e27af87 CANCEL_REMOVE/veto/handle recovery passed, audio-install restart
still blocked. USB peer32f8217 correct data addresses but seven stale sectors/
metadata changes; next submitted buffers/completion tracing unresolved. Root
sent authorized continuations and lease release; root dashboard cold integrity
does NOT resolve peer repeated-boot failure. No candidate integrated. Previous232 summary file-count corrected here: raw
allocation files6724, not6723; original evidence untouched.

--- Previous continuation retained byte-exact below ---

'''.encode()
cont.write_bytes(prefix+old)
(k/'continuation-record001.json').write_text(json.dumps(dict(old_sha256=hashlib.sha256(old).hexdigest(),prefix_bytes=len(prefix),new_sha256=sha(cont),old_tail_preserved=cont.read_bytes()[len(prefix):]==old,physical_access=False),indent=2)+'\n')
print('233 partial evidence and failed protocol report/continuation recorded')
