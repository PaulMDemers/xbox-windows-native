# Initial target-process breakpoint attempt

Exploratory run nt5-video-shutdown-targets-001 watched PspTerminateProcess and
hard-error routines. No event was captured before normal restart and owned
cleanup. Cold artifact checks passed with zero popups, but debugger timing makes
ordinary_boot_qualified false. This run is not a fix or runtime qualification.

Later disassembly shows NtTerminateProcess implements target-thread termination
itself and does not call PspTerminateProcess in this kernel. Therefore this was
the wrong target for resolving the CSRSS handles observed in the earlier run.
The next prepared diagnostic uses the successful handle-reference point inside
NtTerminateProcess instead. This finding does not rule out a process failure.
No physical access or deployment occurred.
