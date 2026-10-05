# Hardware replay procedure

This one-shot hardware run is complete and qualified in
`physical-replay-qualification.json`. Do not relaunch it. The procedure below
documents what was performed. Actual Paint I/O is now recorded in
`paint-sequence-review.json`; `matched-emulator-validation.json` qualifies the
new emulator replay. A separate hardware trial now uses the matched writer:
14 + 40 + 27*16384 byte writes, position query, flush, EOF, close; sixteen cases
alternating detailed logging and quiet target I/O. Its single launch and
collection state are recorded in `physical-matched.json`. Do not relaunch it.
It is now complete and qualified in `physical-matched-qualification.json`:
sixteen exact files, normal restart, no new delayed-write event, full allocation
scan and all 3,439 binaries/nine hives passed. The console is on the dashboard
with no-op startup restored. The next direct repeatability check is a manual
Paint draw/save/reopen session; that next Windows session has not been launched.

`physical-matched.py` implements its separate launch/collection record.
The existing `physical-replay.py` is specific to the completed 64 KiB test and
must not be rerun or pointed at the new binary. The old `/F/xwnpaint` directory,
attempt/replay logs, outputs, and helper hashes are preserved baseline evidence.
The runner hardcodes `C:\xwnpaint\replay.exe` and `attempt.log`. Deployment
verifies all 21 old files and renames the directory to `/F/xwnpaint64`, then
creates a clean `/F/xwnpaint` for the emulator-tested helper and runner.
Collection restores no-op startup first, preserves reports and outputs,
archives this run as `/F/xwnpaint16`, and restores the original directory and
checks all its file hashes. No old logs or user files are deleted. The user's
partial desktop BMP is retained and hash-checked separately.

After collection, run `physical-operation.py postmatched launch` and `collect`
for the independent read-only scanner. Analyze `artifacts/postmatched` into
`physical-matched-allocation.json`; run `audit-restored.py --phase postmatched`.
Decode the four before/after EVT files into `matched-before/after-*` reports,
then run `qualify-physical-matched.py`. An emulator pass and a physical pass
remain distinct, and neither establishes repeated success of actual Paint.

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
sixteen outputs, event logs and current driver hashes.

`runner.c` now implements that launcher using a flushed CREATE_NEW attempt
log and a wait for the writer's exit code. It requests a normal, non-forced
restart only on exit zero; failures leave Windows running and preserve the
log. It has no background timer. `physical-replay.py launch` requires the
completed runner emulator cold audit and normal EventLog stop, verifies the
physical baseline and creates a new test folder. It refuses an existing
launch record or folder. `physical-replay.py collect` restores the no-op
startup first, then preserves evidence and verifies all files and hashes.

After collection, use `native-windows-fatx-recovery/physical-operation.py
postreplay launch` and `postreplay collect` for the existing read-only native
scanner. Analyze its `artifacts/postreplay` capture into this kit's
`physical-replay-allocation.json`. Run `audit-restored.py --phase postreplay`
for the separate binary/hive check. Decode before/after system/application
EVT files, then run `qualify-physical.py`. All are distinct from the earlier
physical Paint and soak reports.

A pass requires all sixteen CASE_PASS records and final PASS, complete matching
BMP bytes after normal shutdown/restart, and post-run allocation/binary/hive
audits. A hang requires preserving the last flushed log and, where obtainable,
thread/resource/I/O state. Missing log lines alone do not identify the blocked
operation: the log writes use the same filesystem and can themselves block.

If the writer passes on hardware, proceed to Paint drawing/save/reopen using
the exact same image geometry and separate new filenames. Add pressure only
after the simpler hardware workload passes. Keep physical and emulator results
separate in all qualification reports.
