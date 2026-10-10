#231 CLOSED: ordered telemetry identifies actual queue backlog

ONE emulator Windows launch accepted 2026-10-10T20:56:01.408112+00:00;
normal dashboard return 2026-10-10T20:57:32.775130+00:00; controller and cold
audit closed 2026-10-10T20:57:54.974062+00:00. No physical access, driver integration or release
tag change. Runtime6823/preparation26006/build6739/host-test8075 are CLOSED;
controller108756/runner114820/tracer112296/
observer112808 are CLOSED. Never replay/recollect this case.

Fresh compiled model changes only diagnostic publication/telemetry. Request1
is release-published; worker/reader state loads acquire; worker final3/4/6
release-publish after existing CAS claim7. Timeout5 withholds the mutable worker
tuple. Actual qemu/atomic.h and compiler.h were compiled unchanged in the host
test; explicit clock/object/string-format/compile-time width adapters surround
the actual report/helper. No stronger atomic mock substitutes. O0/O2 ASan/UBSan
each passed100000 timeout/completion races and10000 publication checks:
checks=1558228 concurrent_pairs=100000 publication_pairs=10000 completed=87594 timed_out=12406 native_grants=0
checks=1559839 concurrent_pairs=100000 publication_pairs=10000 completed=87057 timed_out=12943 native_grants=0
These are host checks, not cross-architecture GPU visibility qualification.
72 actual-helper guard checks and PowerShell syntax passed.

Actual stopped-dashboard request reported state4/refused, reason1,
tuple_published1/version231; surfaces/dirty/downloaded/bytes all0, error0,
references_retired0/native_grant0. GET03fc49b0, PUT03fd4c70, DMA_STATE00000104:
numerical gap66240bytes, parser method-count0/error0. PUSH0/DMA_PUSH/PULL0 and
PGRAPH_FIFO access are1; DMA_PUSH suspended status0. Request and worker-gate
raw snapshots match exactly. Reason1 is therefore GET/PUT inequality at this
gate, rather than a parser error/count. This is no proof of command validity or
successful consumption. The actual pusher and surface predicates are unchanged.
Current diagnostic halts the worker before checking the queued stream.

Correct GDB physical query/set/query and restore/set/query were verified.
212992 actual before/after bytes prove old20KiB RAMIN and84KiB CPU tail unchanged
during this diagnostic phase. No guest breakpoints, memory/register writes,
consuming drain, dirty readback or ownership. See queue-review001.json and
trace001/trace.json. Stable terminal telemetry does not end frontend/backend
references or satisfy the allocator/context/alias prerequisites for native copy.

Unchanged224 CPU workload passed65 allocations/releases,3194880 verified bytes,
65 exposure refusals/four joined workers. Eight rounds/128 immediate MMIO reads
retained UNMODELED_BUSY/NO_OWNERSHIP refusal. Existing211 emulator wizard policy
performed3 actions/idle; no synthetic null-device policy. Normal EventLog6006
count1, dashboard return, no application event delta. Full cold allocation:
320 directories/6724 files/321 directory clusters,0 errors/orphans. Five
structural hives, protected files/startup/history/device-policy checks passed.
This is selected payload/hive integrity, not an all-file-content safety claim.
StrictFALSE: sole inherited Ftdisk49/error3 remains. GPU preservation, ordinary,
physical and native ownership qualification remainFALSE; no gate waived.

Preserved host-only failures: author audit-assert syntax assumption corrected
with byte-identical partial-output resume; test001 lacked host GLib development
package, test002 lacked stripped osdep compile-time assertion adapter. No guest
launched during those failures. Frozen first decoder rejected actual single-bit
shift masks; a NEW bounded decoder002 accepts exact hex or (1<<n), retaining
the original and failure record. No frozen input changed after launch.

Compiled exe SHA256 7b8175c38ae260d11d38fe7c5e4a172b29c17c8c300c7ded84f6bb622bcde89b;
full actual source pins candidate001-source-pins.json; toolchain/source revision
unchanged from228. All five borrowed files restored byte-exact after build.
Private fixture E:/Codex-archive/xbox-windows-native/publication231/
trace001-source.qcow2; private run E:/Codex-private-artifacts/
xbox-windows-feasibility/publication231-runs/nt5-publication231-trace001.
Preserve physicalFATX0101/video0093, original0088 rollback and immutable0.1.0.

Next NEW model must run the actual parser/puller with bounded iterations/words,
real time, real stall telemetry and the guest CPU kept stopped. Never synthesize
empty state, clear errors or resume the producer to force a result. See
CONSUMPTION-NEXT.md. Only actual preserving readback plus independently ended
references can support a later ownership decision.
