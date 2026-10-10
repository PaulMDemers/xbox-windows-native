#233 CLOSED: actual NOP acknowledgement observed; snapshot protocol FAILED

One fresh owned dashboard-only emulator run closed 2026-10-10T22:55:40.376671+00:00.
Build53097/build00265458/preparation56819/runtime44536 CLOSED. Controller
115256/runner114788/tracer113876/observer
111276 CLOSED. Never relaunch/recollect trace001. No physical
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

First live snapshot succeeded: total16682, retained256,
overwritten16426. Captured51 producer1->2 pairs,
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
checks=1395 records=100000 capacity=256 saturation=covered read_only_fill=covered
checks=1395 records=100000 capacity=256 saturation=covered read_only_fill=covered
Tests use actual QEMU atomic headers with explicit clock/register/FIFO and caller
pthread-lock adapters; no actual GPU or QEMU scheduling qualification.72 guard
checks and PowerShell syntax passed. Review001 regex consumed a preceding blank
line; source diff proved that helper's mistake. Failed review source/record kept,
NEW review002 horizontal-whitespace stripper verified ordinary source unchanged.

Actual selected exe SHA256 f032eeae8e82e796b009090a9fde0192d59980443c42d43e2c9a577d9337606c; candidate002-source-pins.json
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
