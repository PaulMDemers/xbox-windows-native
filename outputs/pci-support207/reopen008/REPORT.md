# reopen008: preserved host-observer failure

The new stack observer failed at the first `IoGetDeviceObjectPointer` entry
with `NameError: name 'call' is not defined`. A misindented insertion executed
class-only bookkeeping for an unrelated kernel open. No class call or usable
caller stack was collected. The observer removed every breakpoint and resumed
the guest. The unchanged guest completed its bounded run and was host-closed
at 2026-10-11T03:46:08.822992Z; this was not a normal Windows restart.

The cold allocation, protected-file, five-hive and history checks passed, as
did the target resource installation, lifecycle, invalid-only HAL probes and
cancel/remove checks. The input event pair and Ftdisk49 remain; pending setup
still held restart. These results do not make the failed caller trace usable.

`failure-review001.json` records the failure and cleanup. The draft
`review-evidence001.py` was not executed because its required trace did not
complete. All executed sources and this used fixture are retained unchanged.
The correction is in a fresh `reopen009` attempt, with a host branch regression
check that reproduces this failure and verifies the repaired dispatch paths.
No physical access, guest-policy change or speculative input fix occurred.
