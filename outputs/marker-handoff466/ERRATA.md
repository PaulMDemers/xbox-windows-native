# Preserved diagnostic failures

source-review001 failed its negative-control assertion: the proposed invalid
timestamp high word was zero, which was already the valid value. review002 uses
an actually invalid value. The candidate, marker and decoder were unchanged.

emu001 failed before staging or SITE EXEC because passive FTP data connection
was refused. No candidate ran. A new never-executed seed was staged offline for
emu002; emu001 was not reused or parented.

emu002 captured a successful first marker but then waited at the host harness's
fixed01000000 address. Its actual report allocated the loader at02000000.
The controller timed out; the asynchronous stop response also prevented explicit
breakpoint-removal acknowledgment. The owned process exited normally, destroying
its remaining debugger state. Later guest execution is unobserved. Do not infer
that it stopped before Windows or before the boot device. In particular, the
inherited `stopped_before_boot_device: true` field in emu002/audit.json is a
collector labeling defect and is NOT valid evidence for that failed run. The
raw audit remains unchanged. Its allocation scan is clean; disk bytes changed.

An intermediate user update also prematurely said the loader had been entered;
it was corrected when the timeout was read. emu003 separately proves the loader
and second marker with an actual allocated breakpoint target. No earlier run is
retroactively qualified. transport-tests003's four field-selection checks are
only synthetic address selection; actual runtime authority comes from emu003.
