# Preserved native test harness failure

The single control001 launch returned to the dashboard without creating a report
or any readback files. This is a failed harness attempt, not a GPU coherence pass.
Do not relaunch or recollect it.

The cold audit found clean E allocation, no changes to existing E files, and no
top-overlay ranges anywhere in F. The immutable backing chain was checked.
The launch was accepted at 15:42:11 UTC on October 8, 2026; dashboard return was
observed at 15:42:36 UTC. Both emulator and observer are closed.

The program used WinAPI E paths without mounting E. Installed nxdk WinAPI resolves
these through the DOS device directory, whereas nxdk automatically mounts only D.
The subsequent, separate143 run recorded E initially unmounted, mounted it, and
completed the workload. This supports the missing-mount explanation;142 did not
record its exact early failure status. Both attempts' FTP report transfers failed;
closed-disk collection is the authoritative result.

Source, private pbkit accessor build, artifacts, disk, trace and failure evidence
are retained. No xemu optimization, Windows driver change or physical test occurred.
