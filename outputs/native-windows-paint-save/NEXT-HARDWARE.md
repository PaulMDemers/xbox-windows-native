# Next hardware diagnostic

Preserve candidate0088, the dimensions trace miniport and the physical HAL.
No driver fix follows merely from passing these emulator tests. The physical
Paint hang still lacks a blocked-thread or I/O-completion trace.

Use one bounded write replay before another manual Paint session. The tested
replay executable and deterministic scribble are pinned in
`helper-build-review.json` and `images.json`. The executable expects Windows
`C:\xwnpaint` (dashboard F on this deployment). Its output files and log are
CREATE_NEW, so refuse deployment if any replay output already exists. Keep the
user's partial desktop `untitled.bmp` untouched.

Deployment must verify the ownership marker, launcher/loader, current no-op
startup, filesystem, HAL, current dimensions miniport and preserved old miniport
against the completed physical Paint record. Preserve pre-run event logs and
trace before resetting the known trace seed. Stage only the helper and its
input in the owned test directory; read them back and hash-check them.

For the first hardware replay, run the writer alone, without the emulator's
memory-pressure helper or concurrent Paint. Use a one-shot startup wrapper
with an on-disk attempted marker so a subsequent Windows boot does not
automatically repeat the workload. Do not add a blind reboot timer. On return
to dashboard, restore the no-op startup before collecting the replay log,
sixteen outputs, event logs and current driver hashes. The wrapper and physical
deployment still need implementation and review; no hardware replay is staged
or launched by this kit.

A pass requires all sixteen CASE_PASS records and final PASS, complete matching
BMP bytes after normal shutdown/restart, and post-run allocation/binary/hive
audits. A hang requires preserving the last flushed log and, where obtainable,
thread/resource/I/O state. Missing log lines alone do not identify the blocked
operation: the log writes use the same filesystem and can themselves block.

If the writer passes on hardware, proceed to Paint drawing/save/reopen using
the exact same image geometry and separate new filenames. Add pressure only
after the simpler hardware workload passes. Keep physical and emulator results
separate in all qualification reports.
