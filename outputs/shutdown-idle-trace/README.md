# Hard-error identity in the idle first-install reproduction

## Result

Run 001 launched once at 19:14:17 UTC on 6 October 2026 and returned to the
dashboard at 19:17:23. The exact ordinary idle-package seed was reused without
guest-content edits. The second attachment captured three events: the public
and internal kernel hard-error calls, followed by kernel shutdown. All initial
kernel site bytes were readable and verified on that attachment; there were no
unreadable hits. The fallback for initially unreadable sites was not exercised.

The two hard-error entries observe one error, status `0xc000026b`, from
`rundll32.exe newdev.dll,DevInstall PCI\VEN_1B36&DEV_0005&...\03`.
PID 1004, EPROCESS `0xff9a0540`, and thread `0xff9dd020` match across both.
The caller `0xa007e406` is in the captured and cold-hash-verified win32k image.
At tick 9991 the error is raised; at tick 10249 winlogon enters kernel shutdown
with action 1. These observations do not include the installer's creation,
resume, token closure or termination. The following termination request in the
matched win32k disassembly remains static evidence only.

Cold audit independently finds the same single Application Popup record as
ordinary idle-package 002: DLL initialization failed because the window station
is shutting down. The 120,000 ms idle helper completed, no explicit mapping/BMP
workload ran, and one normal EventLog shutdown preceded dashboard return.
The GPU package installed correctly, with unchanged driver binaries and the
expected reboot-required query-remove veto. Eight staged payloads plus the
idle helper, the reviewed runtime binaries and five structural hives were
checked; see the exact counts in evidence-review.json. Full F: allocation is
consistent: 322 directories, 6,742 files, zero orphans and zero errors.

The result remains **FAIL because of the popup**, and `ordinary_run_valid` is
false because this was debugger-observed. No hardware change, fix, candidate
promotion or recovery capture occurred. The runner, supervisor and both tracer
attachments finished; guest execution was restored before owned cleanup.
The cross-check is reproducible with `review-evidence.py`.

## Next investigation

The minimal first-install reproduction now has an observed error owner. Preserve
this fixture and failure. Focus the next experiment on whether that installer
starts or resumes after GUI shutdown begins, rather than repeating broad
process traces or increasing the idle delay. Previous lifecycle observations
changed the outcome; any new trace must retain its own cold event result and
must not borrow the failing path from this run. A proper device package or
shutdown synchronization change needs reviewed behavior and an ordinary
first-install/reboot control. Removing the device or suppressing its installer
would not establish a fix. This emulator PCI identity is not a finding about
the physical console's popup.

## Method and reproduction

Replay the exact immutable shutdown-install-idle002 fixture and120-second helper,
with no guest-content change. Physical FATX0098/video0093, original0088 rollback
and immutable0.1.0 are unchanged. Unique emulator run/disks/ports and owned leases.

A read-only paused runtime capture identified NT and its actual load base. The
first tracer attachment encountered GDB E14 during initial target-byte reading,
armed no sites, recorded zero events and resumed the guest. Preserve it as
001/trace-early.json with exact trace-early-source.py; do not call it a trace.

A second attachment to the SAME launch records initially unreadable addresses
instead of requiring all target pages readable before arming. It does not force
residency or change guest data/registers/results. Every readable initial kernel
site and every retained breakpoint hit must match reviewed instruction bytes.
Unknown/unreadable hits remain explicit. The pinned cold binary hashes and
runtime kernel base remain independent checks. Both source snapshots are kept.

Only reviewed native/kernel hard-error and kernel-shutdown sites are armed.
The owning command line is read using that process's own page tables, retaining
nonresident data as unknown. Breakpoint pauses/stepping influence scheduling;
ordinary_run_valid stays false even if the cold diagnostic checks pass.
No physical console access or hardware qualification is part of this experiment.

Source/runtime/trace data are under001. Shared site provenance is in
../shutdown-popup-workload/site-review.json and caller-review.json; the local
site-review.json is an exact copy. Audit tools verify completed helper timing,
absence of the mapping workload, exact payload/runtime hashes, five hives,
event deltas, package registration and full read-only F: allocation consistency.
The ordinary pair's strict package failure remains independent of this trace.

prepare.py refuses reusing a seed/manifest. Run.ps1 and supervise.py launch once.
Use shared capture-runtime.py on owned monitor4594 once Windows is running, then
trace.py001 on owned GDB4595. Never rerun a recorded launch. Snapshot tracer
source before execution. Restore guest execution and close owned processes on
completion; cold audit only after cleanup. Raw Windows/disk artifacts stay private.
