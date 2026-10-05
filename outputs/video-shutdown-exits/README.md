# Shutdown process-exit observations

Exploratory run nt5-video-shutdown-exits-001 used unchanged0096 and the original
120-second synchronous startup protocol. Breakpoints captured25 calls to
NtTerminateProcess, including probe exit and CSRSS terminating other processes.
No hard-error call was captured. Target handles from CSRSS were not decoded in
this first trace, and some process parameters were not resident. The trace's
six-word stack snapshots include extra stack words for the two-argument function;
only the first two words are arguments to NtTerminateProcess.

The guest restarted normally and its owned emulator closed. Cold diagnostic
checks passed with zero new popups. Debugger pauses changed timing, so
ordinary_boot_qualified remains false; this is not evidence of a driver fix.
exit-trace.json records connection reset when the supervisor closed the returned
emulator, not a Windows crash. No physical access occurred.

fixture-startup.json records read-only software-hive startup registrations with
password-named values excluded. closed-trace-compression.json documents12 closed
owned CPU logs compressed with byte-for-byte verification, freeing about1GiB.
No disk image, QCOW backing parent or source cache was removed.
