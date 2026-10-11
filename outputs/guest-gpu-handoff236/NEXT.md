#236 CLOSED; next discriminator is GPU state at executing transfer

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

Mask correction from pinned compiled source: bit1=FIFO access disabled, bit2=NOP,
bit4=flip, bit8=context-switch. waits1 has NO context-switch flag. Preserve
old report interpretation failure; phase snapshots should record actual FIFO
access gating, not diagnose a nonexistent context wait.

Keep IRQ timing explicit: disabled FIFO access is sampled mid-handler after
one instruction. Do not label it persistent; observe handler completion and
transfer-phase state independently before selecting a remediation.
