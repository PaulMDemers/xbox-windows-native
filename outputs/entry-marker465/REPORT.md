# 465: bounded early-entry marker core

Host001 passed 32 executions of the actual assembled 32-bit marker and 32
immutable repeated-call checks. The test traps and models CLI, IN, OUT and RDTSC;
it does not perform privileged I/O or attest a physical Xbox LED. General
registers, stack position and the tested arithmetic/direction flags are preserved.

The marker performs two SMC writes: LED pattern register 8, then manual LED
control register 7. It uses one global 4096-read budget and a 64,000,000-TSC-tick
budget. The tick count is not an independently calibrated duration. Busy, errors,
unknown status bits, timeout and a clock earlier than the start refuse without
retry/reset. Only a completed idle status may be acknowledged. The immutable
96-byte record distinguishes started writes from completed transactions.

Sources, executable, 32 records, disassembly and compiler identity are retained
in C:/xwn465/host001 and pinned by host001.json. No physical access, console file
change or boot reliability result occurred in this kit. Integration is separate
in marker-handoff466.
