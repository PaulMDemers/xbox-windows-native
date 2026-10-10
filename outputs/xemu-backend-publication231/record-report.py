"""Write closed231 checkpoint and prepend continuation without changing old bytes."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'REPORT.md';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=read(k/'trace001/host-state.json');a=read(k/'trace001/audit.json');q=read(k/'queue-review001.json');b=read(k/'build001.json')
assert h['closed'] and a['cpu_scope_passed'] and a['integrity_passed'] and q['passed']
launch=read(k/'trace001/launch.json')['cycles'][0]
tests=read(k/'publication-test003.json')['runs']
dest.write_text(f'''#231 CLOSED: ordered telemetry identifies actual queue backlog

ONE emulator Windows launch accepted {launch['launch_requested_utc']};
normal dashboard return {launch['dashboard_return_utc']}; controller and cold
audit closed {h['closed_utc']}. No physical access, driver integration or release
tag change. Runtime6823/preparation26006/build6739/host-test8075 are CLOSED;
controller{h['controller_pid']}/runner{h['runner_pid']}/tracer{h['tracer_pid']}/
observer{h['observer_pid']} are CLOSED. Never replay/recollect this case.

Fresh compiled model changes only diagnostic publication/telemetry. Request1
is release-published; worker/reader state loads acquire; worker final3/4/6
release-publish after existing CAS claim7. Timeout5 withholds the mutable worker
tuple. Actual qemu/atomic.h and compiler.h were compiled unchanged in the host
test; explicit clock/object/string-format/compile-time width adapters surround
the actual report/helper. No stronger atomic mock substitutes. O0/O2 ASan/UBSan
each passed100000 timeout/completion races and10000 publication checks:
{tests[0]['stdout'].strip()}
{tests[1]['stdout'].strip()}
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

Compiled exe SHA256 {b['executable_sha256']};
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
''',encoding='utf-8')
coord=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),audio=dict(thread_id='01a122df-2515-7771-af51-845a17aef351',title='Xbox Windows 2000 audio',cursor='fc98851a-68a5-49a8-880b-c5efa3c3b0fe:3',state_at_check='idle unchanged',physical_evidence_commit='5fbcc971',audibility='unknown'),pci=dict(thread_id='01a122e0-8af9-7701-b31d-bb5d044829b3',title='Xbox Windows 2000 PCI devices',cursor='a359a01f-3975-433e-959d-e708e52252e0:13',commit='09430b6',reported='HAL boot/API/power/removal/cold checks pass; normal restart blocked pending audio install; SMBus functional reads and terminal takeover untested',followup_sent='Continue independent SMBus checks; preserve failure gates, no integration'),usb=dict(thread_id='01a122e0-90d9-7cc3-9457-867066f7dd06',title='Xbox Windows 2000 USB and gamepad',cursor='20229634-e36a-47d4-9b39-24f2193d22e6:8',reported='Repeat-boot storage failure unresolved; preserve both disks',followup_sent='Matched second-boot baseline without XID; no physical changes/integration'),root_lease_released=True,physical_integration=False)
(k/'coordination001.json').write_text(json.dumps(coord,indent=2)+'\n')
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes()
prefix=f'''# Current:231 CLOSED ordered telemetry; actual queued GET/PUT gap identified

Read outputs/xemu-backend-publication231/REPORT.md, queue-review001.json and
CONSUMPTION-NEXT.md. Fresh model/source/exe pins, actual QEMU atomic host tests
and one stopped-dashboard request. State4/reason1, GET03fc49b0/PUT03fd4c70,
66240-byte numerical gap; parser count/error0, FIFO accesses1, DMA suspended0.
Request/gate words identical. No queue consumption, dirty readback, reference
retirement or native grant.212992 before/after raw reserved bytes unchanged.
Release/acquire terminal telemetry implemented; timeout mutable tuple withheld.
Actual pinned QEMU atomic headers tested O0/O2: each100000 timeout races plus
10000 publication pairs, ASan/UBSan clean. No stronger atomic mock.

ONE launch20:56:01UTC, normal dashboard20:57:32, closed/audited20:57:54 Oct10.
CPU65 allocations/releases/3194880bytes/four joined workers and refusal scope
PASS. Cold320dirs6724files321clusters,0errors/orphans; five hives/protected/
startup/history/device policy PASS. StrictFALSE soleFtdisk49/error3; backend/
ordinary/physical/native FALSE. Preserved host author/test001/test002/decoder
failures; frozen inputs unchanged. ALL root owned sessions CLOSED: build6739,
host8075, prep26006, runtime6823; controller108756/runner114820/tracer112296/
observer112808. Private fixture/run paths and executable pin in REPORT.
20GiB guard retained, no physical FTP/deploy, no candidate merges/tag changes.

Next NEW model: finite genuine parser/puller consumption with stopped vCPU,
waiting flags and raw before/after telemetry. Budget jumps/packets/time and
respect flip/context/nop stalls. No fake idle/error clearing or producer resume.
Preservation and ended reference/census/private-context/alias gates remain.
Never relaunch/recollect231 or previous closed230/229/228/227.

Check-in: audio unchanged idle/5fbcc971, audibility unknown. PCI09430b6 reports
HAL API/lifecycle/cold passes but audio setup blocks normal restart; SMBus and
terminal takeover untested. USB reports repeat-boot storage failure; root fresh
first-boot PASS does not resolve it. Authorized follow-ups sent for independent
SMBus and matched no-XID second-boot control; preserve their strict failures
and physical baseline, root leases free. See coordination001.json.

--- Previous checkpoint retained byte-exact below ---

'''
p.write_bytes(prefix.encode('utf-8')+old)
(k/'continuation-record001.json').write_text(json.dumps(dict(previous_continuation_sha256=hashlib.sha256(old).hexdigest(),prefix_bytes=len(prefix.encode('utf-8')),continuation_sha256=sha(p),report_sha256=sha(dest),owned_root_sessions_closed=True),indent=2)+'\n')
print('231 report and exact continuation recorded')
