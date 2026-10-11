"""Record closed evidence and replace pending continuation, preserving prior tail."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
t=read(k/'trace001/trace.json');a=read(k/'trace001/audit.json');h=read(k/'trace001/host-state.json');q=read(k/'review001.json');allocation=read(k/'trace001/allocation.json')
assert h['closed'] and q['passed'] and read(k/'process-closure001.json')['owned_processes_absent']
assert not (k/'REPORT.md').exists()
ack=t['completed_write_corroboration'];writer=q['writer'];xe,fe=t['events'][1:];w=a['workload'];ret=a['retirement']
report=f'''#236 CLOSED: dashboard IRQ and actual loader entries pinned

Single fresh standalone211 child, unchanged234 executable
7d953556b2bd4155f43779250fb2240e5d8f7f656525e9c33fdbad6ccf1a976e,
unchanged224 CPU manager/219 bootvid/211 captured physical-core policy;
NO synthetic null bindings. No emulator build, driver changes, physical IO,
device integration or release tag change. Preparation59031 CLOSED0; runtime
70400 CLOSED0 at{h['closed_utc']}; all root owned processes absent and leases
released. Never relaunch/recollect236 trace001 or failed235 trace001.

See [actual trace](trace001/trace.json), [review](review001.json),
[cold audit](trace001/audit.json), [allocation](trace001/allocation.json),
[closed host record](trace001/host-state.json) and [design](DESIGN.md).
Private runtime E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-runs/
nt5-guest236-trace001; immutable seed E:/Codex-archive/xbox-windows-native/
guest236/trace001-source.qcow2, exact hash in fixture-trace001.json.

## Guest acknowledgement

After-write GDB watchpoint fd400100/4 stopped at NEXT EIP
{t['events'][0]['post_write_eip']:#x}. Reconstructed unique preceding candidate
{writer['address']:#x}, bytes`{writer['hex']}`, `{writer['mnemonic']} {writer['operands']}`:
ESI=fd000000, EAX=00100000, effective NV_PGRAPH_INTR addressfd400100.
Entire resident64-byte code window matches exact cold dashboard XBE. This
establishes binary origin, not a handler source symbol; the instruction-start
boundary is reconstructed from next EIP/registers/code and journal correlation.
Operand/segment/repetition-prefix suffixes and unknown registers are refused.

ONE immutable234 worker snapshot: total{ack['header']['total']}/count256,
{ack['header']['overwritten']} overwritten, lost prefix unknown. Last guest
ack rows{ack['ack_before'][0]}/{ack['ack_after'][0]} matchvalue00100000,
pending00100000->0, waits{ack['ack_before'][9]}->{ack['ack_after'][9]}:
NOP clears, context-switch wait remains. Current copied PG-only row also
waits{ack['current_pg_only'][9]}, FIFO-invalid. GPU worker may progress while CPU
stopped; this current row is not a fresh sample at either loader entry.
No preserve232 request, wait clearing/reset, native grant or dirty readback.

## Actual transfer

Trace alone owned readiness and ONE accepted loopback SITE EXEC. Entry stops:
- Xromwell XBE EIP{xe['registers'][8]:#x};32 executing bytes match cold XBE,
  SHA{xe['pin']['sha256']}; EFLAGS{xe['registers'][9]:#x}.
- FreeLoader multiboot EIP{fe['registers'][8]:#x};32 executing bytes match cold
  freeldr.sys, SHA{fe['pin']['sha256']}; EAX{fe['registers'][0]:#x},
  EBX{fe['registers'][3]:#x}, EFLAGS{fe['registers'][9]:#x}, IF clear.

Multiboot magic and disabled CPU interrupts are actual register observations;
they do not establish GPU producer quiescence, queued-work/reference retirement,
safe instance-memory ownership or firmware object release. The snapshot belongs
to prelaunch dashboard time. Historic source/packaging leads are not claimed to
be clean source rebuilds of these owned binaries.

Both instruction breakpoints and write watchpoint removed exactly once. GDB
read mode remained0, no debugger memory/register writes, no remaining points,
guest resumed; all interpreted resident pins independently rechecked. Debugger
timing makes this a diagnostic, not an ordinary performance run.

## Windows and recovered-image checks

Single normal shutdown6006=1 and dashboard return. CPU{w['allocations']}
allocations/{w['releases']} releases/{w['exposure_refusals']} exposure refusals,
{w['verified_bytes']} exact bytes, {w['joined_workers']} joined workers passed.
Eight retirement rounds/{ret['reads']} sequential MMIO reads retain
UNMODELED_BUSY/NO_OWNERSHIP; no command writes or GPU ownership qualification.
Cold{allocation['directories']} dirs/{allocation['files']} files/
{allocation['directory_clusters']} directory clusters, zero errors/orphans;
five structural hives, protected hashes, startup, history and selected policy
passed. No application events; strict failure remains Ftdisk49/type1.
CPU/observation/guest trace TRUE; strict overall FALSE, ordinary/physical GPU
qualification FALSE. No gates waived or Ftdisk claim revised.

Inherited runner ends via host vm.Kill after capture. This cold audit describes
the recovered QCOW image, selected contents and metadata. It is not all-file
content safety, completed emulator-cache flush, or repeated-boot qualification.
The USB chat's separate orderly-exit control investigates stale forced-stop
images; its results are neither integrated nor silently applied to this run.

## Reviewed harness correction and retained failures

235 preserved partial IRQ proof but loader login421 failed BEFORE SITE EXEC:
observer occupied dashboard's sole FTP connection.235 cold integrity passed,
no Windows/workload/new events; all corresponding scopes FALSE.236 removes
observer prelaunch FTP entirely; trace is sole readiness/launch owner.
Actual supervisor-source adapters12 checks cover accepted/pass, accepted/failed
diagnostic, unaccepted launch and unsafe cleanup without any prelaunch
connection. Parser57 and guard72 checks passed; PS syntax and prelaunch review
passed.236 frozen464 pins and235 frozen467 pins independently unchanged.
235 host test001 wrong XBE field offset and002 wrong immediate ambiguity
expectation preserved with original source; corrected003 also refuses override
suffix proof. Resource-only busy attempts precede unique starts; never repeat a
started preparation/launch/collection.

Next is phase-specific GPU state at these now-pinned transfer points. Preserve
physical0101/video0093,0088rollback,immutable0.1.0 and all failed evidence.
No acceleration or extra video mode is qualified by this diagnostic.
'''
(k/'REPORT.md').write_text(report)
(k/'NEXT.md').write_text('''#236 CLOSED; next discriminator is GPU state at executing transfer

All root processes CLOSED; no new experiment running. Never relaunch/recollect
235/236 trace001. Read REPORT.md, review001.json and actual raw/cold records.

Actual dashboard IRQ bytes are pinned at14b1b1 (next EIP14b1b7), NOP ack clears
waits3->1. Actual Xromwell entry11100 and FreeLoader multiboot200a20 pinned;
FreeLoader EAX2badb002 and IF0 observed. Snapshot234 is ONE prelaunch immutable
copy, NOT a transfer-phase observation. CLI/entry alone cannot close GPU gates.

NEW bounded phase-sampling kit should associate independent immutable worker
copies with before-launch, executing XBE entry and executing FreeLoader entry.
Do not reuse one-shot snapshot234, reset its state or relabel its old tuple.
If the provider is extended, use finite independently owned slots with the
same CAS publication, terminal timeout/late-copy hiding, explicit phase and
FIFO-validity labels; host-test races/immutability and restore borrowed source.
Keep compiled exe/input pins, exact entry bytes, complete debugger teardown,
unique fixtures and cold/event audits. No speculative firmware/driver changes,
forced wait clearing, renderer reference disposal or GPU ownership grant.

Identify actual pending/wait/FIFO and referenced dirty-surface/context state at
the transfer boundary before proposing producer close or backend preservation.
Dirty readback, reference retirement, instance allocator and alias coherence
remain unresolved. Further static loader source leads must match executing
owned bytes; no clean historical binary reconstruction claim.

Retain recovered-image vs completed-emulator-flush distinction: root harness
uses host vm.Kill after capture. USB's separately controlled orderly exit must
be reviewed on its own evidence; don't change launch closure silently to PASS.
CPU/trace/integrity PASS; strictFALSE sole inherited Ftdisk49; no ordinary or
physical GPU qualification. Keep physical0101/video0093,0088rollback,immutable
0.1.0 and failed evidence. Root made no physical IO or peer driver integration.
''')
p=ws/'outputs/engineering-notes/CONTINUATION.md';prior=p.read_bytes();meta=read(k/'progress001.json');tail=prior[meta['new_prefix_bytes']:];assert hashlib.sha256(tail).hexdigest()==meta['previous_continuation_sha256']
prefix=f'''# Current: guest236 CLOSED; dashboard IRQ and actual loader entries pinned

Read outputs/guest-gpu-handoff236/REPORT.md, DESIGN.md, NEXT.md, review001.json
and actual trace001 records. Latest head before turnbc81cb6. Root235/236 owned
sessions58795/95616/59031/70400 CLOSED; all recorded PIDs absent, leases released.
236 closed{h['closed_utc']}; no new root experiment running. Never relaunch or
recollect235/236 trace001. NO root physical IO, device integration/tag change.
Physical0101/video0093,0088rollback,immutable0.1.0/all failures preserved.

Unchanged234 exe7d953556...;224 CPU/219 bootvid/211 captured physical-core policy,
no synthetic null bindings. Dashboard cold bytes match reconstructed writer
14b1b1/nextEIP14b1b7; value100000 matches last journal ack, waits3->1/context
wait remains. ONE immutable prelaunch snapshot total{ack['header']['total']}/256,
overwritten{ack['header']['overwritten']}; not a GPU sample at loader transfer.
Actual Xromwell entry11100 and FreeLoader multiboot200a20 resident32-byte pins
match owned binaries; EAX2badb002,IF0 at FreeLoader. This proves CPU transfer,
not producer close/reference retirement/dirty readback/instance ownership.
Full debugger teardown/mode0/no writes/resumed. CPU65 allocations/releases/
refusals,3194880 bytes/four workers PASS;8 MMIO rounds128 reads still refuse
UNMODELED_BUSY/NO_OWNERSHIP. Normal6006=1/dashboard, cold320dirs/
{allocation['files']}files/321clusters,0errors/orphans,5hives/protected/history/policyPASS.
CPU/observation/traceTRUE; strictFALSE soleFtdisk49; no application events.
Inherited host runner forced exit: cold evidence is recovered-image scope,
not all-file-content/cache-flush/repeated-boot safety.

235 CLOSED partial IRQ proof, loader login421 before SITE EXEC because observer
held sole FTP connection; no Windows/workload, coldPASS/scopesFALSE.236 removes
prelaunch observer FTP; connection12/parser57/guard72 tests and PS/prelaunch
PASS,464 frozen pins unchanged (235467 unchanged). Both235 failed host test
expectations preserved. Next NEW finite immutable phase snapshots at these
executing entry points; never reuse published234 slot or force wait clearing.
Peer audio channel test preparation, PCI input-port trace, USB orderly-exit
control continue separately. No peer integrated; unresolved peer gates retained.

--- Previous continuation retained byte-exact below ---

'''.encode()
p.write_bytes(prefix+tail)
(k/'continuation001.json').write_text(json.dumps(dict(passed=True,previous_tail_sha256=hashlib.sha256(tail).hexdigest(),pending_note_sha256=hashlib.sha256(prior).hexdigest(),new_prefix_bytes=len(prefix),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physical_access=False),indent=2)+'\n')
print('236 report/NEXT/continuation recorded; old tail exact')
