# Crash-dump configuration diagnostic

This kit contains five distinct, single-launch emulator diagnostics of the
unchanged FATX0101/video0093 baseline, with the evidenced missing HidServ
executable restored exactly as in baseline-hid-restore. These are debugger
observations, not ordinary performance tests or physical qualification.
Every child starts from the same settled emulator parent, preserving its
synthetic null-device and unsupported-device policy. No driver, registry,
service, dump policy or physical device was changed.

The important trace is serial005/trace.json: the crash-dump usage notification
is forwarded by VfatPnp to Ftdisk and returns pending, then IopSynchronousCall
returns STATUS_NOT_SUPPORTED. The earlier disk queries, dump pointers and
miniport dump-driver load succeed. No IopCompleteDumpInitialization call or
FSCTL_QUERY_RETRIEVAL_POINTERS occurs on this failing path.

Read REPORT.md and NEXT.md. Do not relaunch or recollect these cases. Source
snapshots in each preflight record preserve the exact script version for its
attempt. Later tracing changes never alter older run evidence. Current entry
points are intentionally restricted to already occupied case IDs; any future
experiment requires a new reviewed ID/fixture and must not overwrite these.
Private guest disks, executables, hives and raw logs remain excluded from Git.
