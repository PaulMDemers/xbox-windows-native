# Next bounded concurrency test

Both cases in this kit are CLOSED. Read REPORT.md and comparison.json. Never
relaunch/recollect them. serial001 passes workload/cold integrity but strict
events fail. flush001 exits on missing overlap in file-round1, with clean cold
allocation and exact completed round0 bytes; it did not finish the workload.

Use a NEW kit/IDs from the same settled0101/video0093 parent. Preserve every
source/binary pin and inherited emulator policy. The2ms window can miss a full
volume flush. Provide a bounded rendezvous while a mapping is dirty: require
the worker to complete a flush within the same unique append epoch and enforce
a deadline. Keep separate freely racing appends to exercise unmap/shrink too.
Use a matching serial control and report the changed schedule explicitly.
Do not call a rendezvous proof of simultaneous kernel instruction execution.

All failure paths must signal the flusher and bounded-join it, retaining errors
and timeout rather than letting ExitProcess silently kill it. Never relax the
per-file-round overlap, shrink, byte, allocation, shutdown or event gates.
No speculative driver patch. Emulator-only until13:00UTC Oct7; preserve physical
0101/video0093,0088rollback,immutable0.1.0. Original physical non-ASCII prefix
and initial restart method remain unresolved. See ../fatx-prefix-forensics.
