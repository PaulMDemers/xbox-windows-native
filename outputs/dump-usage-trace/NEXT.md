# Next discriminator

Both dispatch001 and dispatch002 are CLOSED. Never relaunch/recollect them.
Read REPORT.md, trace-verification.json, hal-source-audit.json and raw records.

Ftdisk49's cause is now explained: current fixed-root HAL supports paging usage
only, completing dump usage with inherited STATUS_NOT_SUPPORTED. No FATX data
corruption was reproduced. Do not patch Ftdisk or FSCTL handling based solely on
the event. Do not remove the event by disabling dumps or returning fake success.

Useful next work is a bounded crash-dump capability implementation in a NEW
isolated HAL source/build and emulator child, if the full root contract can be
satisfied: separate balanced dump-path accounting, no stop/remove or power-down
while active, resident dispatch/code, preserved paging behavior and explicit
hibernate non-support. Review existing root PDO power handling and source/build
provenance first. Compile/test real handlers and import/section identities.
Do not modify the installed physical HAL or settled fixtures.

Then observe actual dump-configuration progress with pinned calls and full cold
audits; treat any next unsupported stage as a new finding, not permission to
force success. Actual controlled dump write/recovery on a sacrificial child is
needed before claiming dump support. Ordinary regressions retain strict event
gates. If implementing the contract is not justified, retain strict failure and
report unsupported dump capability explicitly, without calling it a storage
corruption regression. The original hardware anomaly still needs its own
specific discriminator.

Emulator authorization ends 2026-10-07 13:00 UTC. Check time before experiments;
at cutoff clean owned processes, preserve evidence, report and pause automation.
No physical FTP/deploy/test. ALL current owned sessions are closed, including
audits54330/61427 and evidence23117. Frozen-source snapshots, private disks and
closure hashes are preserved. No new HAL candidate has been built in this kit.
