# Video timer and bus-entry observation684

This is a prerequisite for native Xcalibur work after the closed kernel display
baselines682/683. It does not resume the parked network probe, program the
encoder, switch video mode, or start Windows.

`main.c`, `sample.h`, and `io.c` build a small nxdk utility. It records raw32-bit
reads from port0x8008 alongside kernel QPC, kernel interrupt time, and RDTSC:
65 immediate samples followed by65 samples separated by100ms kernel sleeps.
Raw values retain all high bits. Each row brackets the other clock reads with
two port reads; the samples are not simultaneous. QPC's independence from the
port timer is unknown, and RDTSC is not serialized. Interrupt time provides a
coarse elapsed-time comparison, not microsecond calibration.

The utility also reads16-bit SMBus status at0xc000 on entry and after sampling.
It issues no SMBus commands, acknowledges no pending status and changes no
interrupt state. Kernel ownership remains active; these observations cannot
prove that a later native handoff will inherit the same state or own the bus.

Two exclusive E-root reports capture `before_samples` and `restart_requested`.
Each report is flushed, closed and read back by the utility. It requests a
firmware restart after about6.4 seconds of sampling. File, kernel sleep and
firmware services are not independently time-bounded. There is no startup hook,
display pattern, LED encoding, or network code in the utility.

`test_sample.c` tests finite acquisition, full-width preservation and argument
rejection. `io_review.py` executes the actual nxdk COFF port-read functions with
Unicorn callbacks, checking ports, instruction widths and absence of writes.
Those are host checks, not hardware clock evidence.

`delay_candidate.h` is a separate HOST-ONLY integer500us candidate. It is not
linked into the console utility. It assumes a qualified32-bit3,579,545Hz timer,
requires1790 ticks, limits reads and rejects backwards samples or large gaps.
Its qualification argument is a caller precondition, not a self-calibration.
`test_delay.c` tests simulated steps/wraps, stalled clocks and rejection paths.
Native compiled-code and physical delay validation are still required before
integrating it with681's checked block protocol.

## Evidence and next step

Use the actual build, host, launch and collection receipts in this directory;
this source description does not itself establish that any test ran. Shared
build-lock refusals are preserved separately and must not be mistaken for
compiler/test failures. No lock is overridden.

After collecting684 once, use measured timer width/rate and raw status to decide
the next native binding. Do not import SDK framebuffer/register state as a
recipe or clear unknown pending SMBus status to pass admission. The first native
encoder trial remains a separate watched pattern-only test before Windows.

Protocol/context references are the pinned source in [681](../xcal681/NEXT.md),
the retained default720 source at launcher677-validation002, and the primary
[Cromwell timer implementation](https://github.com/XboxDev/cromwell/blob/master/drivers/pci/BootInterrupts.c).
