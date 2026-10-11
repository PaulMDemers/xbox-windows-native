#235 CLOSED partial guest IRQ proof; loader launch host failure

ONE fresh emulator attempt, unchanged234 exe /224 CPU payload/219 bootvid/211
physical-core device policy; no synthetic null binding, driver changes or
physical access. All sessions58795(preparation)/95616(runtime) CLOSED. Actual
host controller closed 2026-10-11T00:41:31.558178+00:00; full debugger teardown, GDB mode0,
no memory/register writes, no remaining breakpoints; guest resumed before owned
capture cleanup. No Windows launch, workload, normal shutdown or new events.

Watchpoint stop `T05thread:01;watch:fd400100;` reports next instruction EIP
`0x14b1b7`. Unique bounded preceding candidate
`0x14b1b1` bytes`898600014000` is
`mov dword ptr [esi + 0x400100], eax`, ESI=0xfd000000,
EAX=0x100000. Entire64-byte resident code window matches exact
owned cold dashboard XBE, SHAbffbb09621b3251619a6a24ac49034c0b85ff117046c3a422462ca8b5a5d9aa0. Instruction boundary
is reconstructed from post-write EIP, not a debugger-supplied instruction-start
PC. Prefix/suffix ambiguity is conservatively refused; no handler symbol or
clean dashboard source reconstruction is claimed.

ONE immutable234 snapshot published. Last guest journal rows
15156/15157 match value0x100000, pending0x100000->0,
waits3->1: NOP wait cleared, context-switch wait remains. Current copied PG-only
row also waits1, FIFO-invalid. Ring total15157/count256,
14901 overwritten; lost prefix unknown. No producer close,
GPU retirement, FIFO drain, ownership grant or dirty-surface readback follows.

Trace then armed Xromwell entry and requested an FTP login. Supervisor still
held its readiness connection, so dashboard rejected the second connection
with421 Too many users BEFORE SITE EXEC. loader_launch status=requesting is
not accepted; Xromwell/FreeLoader entries NOT observed. Observer rejected this
failed launch; controller closed/audited once. Runtime trace/CPU/overall scopes
remain FALSE, not interpreted as a guest boot failure.

Cold F: 320 dirs/6719 files/
321 directory clusters, zero errors/orphans; five hives,
protected hashes/startup/history/device-policy passed. This is metadata/selected
file integrity, not all-file-content safety or repeated-boot qualification.

Host parser00357 checks and guard72 checks passed. Failed test001 used XBE
0x110 instead of0x10c; failed002 incorrectly expected immediate-MOV ambiguity.
Exploratory decoder output exposed override suffix acceptance; corrected parser
conservatively refuses prefix-valued boundaries. Both original test sources and
failure records preserved;467 frozen pins unchanged. Preparation resource-only
busy attempts1-4 and runtime resource-only attempts1-4 preceded single starts.

Next: NEW independent guest236 child fixes observer connection ownership;
never relaunch/recollect235. It adds actual-source connection adapter tests,
keeps the same watchpoint/entry bounds and strict cold/event/ownership gates.
Physical0101/video0093,0088rollback,immutable0.1.0/all failures preserved.
