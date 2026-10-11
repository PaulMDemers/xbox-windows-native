#236 CLOSED: dashboard IRQ and actual loader entries pinned

Single fresh standalone211 child, unchanged234 executable
7d953556b2bd4155f43779250fb2240e5d8f7f656525e9c33fdbad6ccf1a976e,
unchanged224 CPU manager/219 bootvid/211 captured physical-core policy;
NO synthetic null bindings. No emulator build, driver changes, physical IO,
device integration or release tag change. Preparation59031 CLOSED0; runtime
70400 CLOSED0 at2026-10-11T00:49:38.536876+00:00; all root owned processes absent and leases
released. Never relaunch/recollect236 trace001 or failed235 trace001.

See [actual trace](trace001/trace.json), [review](review001.json),
[cold audit](trace001/audit.json), [allocation](trace001/allocation.json),
[closed host record](trace001/host-state.json) and [design](DESIGN.md).
Private runtime E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-runs/
nt5-guest236-trace001; immutable seed E:/Codex-archive/xbox-windows-native/
guest236/trace001-source.qcow2, exact hash in fixture-trace001.json.

## Guest acknowledgement

After-write GDB watchpoint fd400100/4 stopped at NEXT EIP
0x14b1b7. Reconstructed unique preceding candidate
0x14b1b1, bytes`898600014000`, `mov dword ptr [esi + 0x400100], eax`:
ESI=fd000000, EAX=00100000, effective NV_PGRAPH_INTR addressfd400100.
Entire resident64-byte code window matches exact cold dashboard XBE. This
establishes binary origin, not a handler source symbol; the instruction-start
boundary is reconstructed from next EIP/registers/code and journal correlation.
Operand/segment/repetition-prefix suffixes and unknown registers are refused.

ONE immutable234 worker snapshot: total14607/count256,
14351 overwritten, lost prefix unknown. Last guest
ack rows14606/14607 matchvalue00100000,
pending00100000->0, waits3->1:
NOP clears, FIFO access remains disabled. Current copied PG-only row also
waits1, FIFO-invalid. GPU worker may progress while CPU
stopped; this current row is not a fresh sample at either loader entry.
No preserve232 request, wait clearing/reset, native grant or dirty readback.

## Actual transfer

Trace alone owned readiness and ONE accepted loopback SITE EXEC. Entry stops:
- Xromwell XBE EIP0x11100;32 executing bytes match cold XBE,
  SHAc8e2d5c1263049464ac45591b83f1203b502b120832c86ee1c04e3588db17f51; EFLAGS0x246.
- FreeLoader multiboot EIP0x200a20;32 executing bytes match cold
  freeldr.sys, SHAbafdf31ce71416d0b51f3ba14aa6d14a3b61015cbec5576c424b8f8f7bb662a5; EAX0x2badb002,
  EBX0x229800, EFLAGS0x46, IF clear.

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

Single normal shutdown6006=1 and dashboard return. CPU65
allocations/65 releases/65 exposure refusals,
3194880 exact bytes, 4 joined workers passed.
Eight retirement rounds/128 sequential MMIO reads retain
UNMODELED_BUSY/NO_OWNERSHIP; no command writes or GPU ownership qualification.
Cold320 dirs/6725 files/
321 directory clusters, zero errors/orphans;
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

Wait-label source review corrected the original report: bit1 denotes disabled
PGRAPH FIFO access; context-switch wait is bit8 and is NOT set in waits1.
Original report bytes and failed interpretation record remain preserved.

FIFO access disabled is sampled with the CPU stopped immediately after the
acknowledgement, before the dashboard handler returns. It may be a transient
handler gate; this capture does NOT diagnose a persistent FIFO stall.
