# Controlled loss of guest state during an actual installer append

This emulator-only diagnostic uses the same immutable aligned input and pinned
FATX0101/video0093 binaries as the completed normal-shutdown control in
`../fatx-paging-buffer/002`. It changes no driver or guest data.

`trace.py` observes the actual mapped paging-write buffer and VfatWrite return.
It stops only after the exact 109-byte suffix at offset270336 reports success
with Information109, provided no write overlapping the preceding111 target
bytes has been observed. At that return breakpoint it removes all breakpoints,
verifies that the guest is paused and sends HMP `quit` while GDB remains attached.
It never steps, resumes or detaches the guest at the accepted checkpoint.

This deliberately prevents Windows normal shutdown. HMP exit lets the host
emulator close its disk; this differs from pulling physical power or killing the
host. The existing runner notices its owned emulator exit and performs cleanup;
its nonzero "Task emulator exited" result is retained, not called a normal boot.
Only after cleanup may the read-only cold auditors open the overlay.

`supervise.py` launches once through localhost4596, waits for the tracer and
records cleanup. It never accesses physical-console FTP or relaunches. Failure
to meet the checkpoint is retained as a failed diagnostic. The tracer has a
600-second/100000-hit bound; runner lifetime is1200seconds.

Cold evidence checks the file's own FAT chain, target raw bytes, source buffers,
selected binary hashes, five hive structures, event deltas and full allocation.
Missing normal shutdown or unfinished installation are expected properties of
this intervention and remain failures of ordinary qualification. A matching
111/109 split would establish a fixture mechanism, not the cause or restart
method of the original physical incident.

Commands, once per unique attempt:

1. WSL `prepare.py 001`, then `audit-before.py 001`.
2. PowerShell `Run.ps1 -Case 001`, then Python `trace.py 001` and `supervise.py 001`
   with the established localhost emulator credential environment.
3. After all owned sessions exit: WSL `audit-allocation.py 001` and
   `audit-interruption.py 001` using the existing private hivex runtime.
4. Review reports, run `verify-evidence.py`, repository checks, commit and push.

Case002 uses a new overlay and the later1524-byte write at the same page offset,
with the same exact109-byte suffix and no preceding prefix write observed.
This checkpoint was selected from the completed normal002 trace to examine
whether file-size publication precedes prefix writeback. Case001's exact tracer
source and failed file-visible reproduction remain preserved independently.

Private
buffers, logs, disks and hive bytes stay outside Git. Preserve every attempt.
