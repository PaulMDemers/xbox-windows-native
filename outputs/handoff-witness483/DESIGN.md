# Later handoff witness

The closed478 success and481/482 failures have identical normalized preparation
records. The new diagnostic observes a later boundary, without changing the
original Windows payload, copied privileged loader, original allocations, or
baseline launcher. It is not a boot fix or ordinary-boot qualification.

The existing report, comparisons and bounded marker execute first. At the old
register-restore point, a branch enters appended code in the same XBE section.
It snapshots the completed primary close, copy eligibility, actual allocations,
completed marker and original saved register/flag frame into a256-byte record.
It exclusively creates handoff.bin, writes once, flushes once and closes once.
Pending, stale IOSB, wrong byte counts or any nonzero status refuses. Current
handle/IOSB storage is reused only after the original primary close completed;
refusal reasons13..19 identify the witness lifecycle. Existing reasons1..12 and
the primary report keep their original meaning. No accepted call is retried.

After witness close, compare the payload and both complete1024-byte loader
copies, including the two patched far targets, again. Only then restore the
original pushad/pushfd frame and jump. No kernel or SMBus call follows those
comparisons. Refusal retains the original one-attempt fallback logger and reboot.

There is insufficient spare space before the original payload. Therefore the
new code/data are appended at file offset0x84000, after the complete original
payload and zero padding. Image size, section virtual/raw sizes and SHA1 digest
are updated. Original entry/thunks, font, payload offset/bytes and loader symbols
are checked independently. This increases the loaded section and adds I/O: it
can perturb timing/allocation and must never be described as an unchanged boot.
The full source reconstructs482 after undoing the explicit branch/include and
namespace substitutions. Upstream wrapper/addition remains GPL-2.0-or-later.

A cold valid witness establishes only the preceding boundary. It cannot prove
its own flush/close, later comparisons, paging transition, payload entry or
Windows startup. A complete witness can coexist with a later refusal; tests
explicitly preserve that distinction. Missing files cannot establish which
unobserved step failed. Calls are bounded in count; synchronous Xbox kernel I/O
has no independently enforceable wall-clock cancellation guarantee. The host
observer has a480-second deadline and must retain an unreturned attempt.

Host validation executes assembled x86 with modeled allocation/kernel/file/SMBus/
TSC effects, trapping CLI before executing the privileged loader.132 paths include
104 inherited cases and28 new cases (27 refusals, one DF-restoration success).
It is not hardware proof or sanitizer coverage. Independent decoding tests actual
host output, truncation, fixed fields, marker semantics and refusal combinations.

One fresh owned physical483 launch is permitted after package freeze: same480
depth sample, new483 controller namespace,90-second sample deadlines and normal
Windows restart. Single SITE reply deadline20seconds; never resend. Fresh E app,
kit, result and hook, complete readback, original720p baseline and module pins.
Remove temporary hook FIRST after dashboard return, collect all three diagnostic
files twice, audit selected hives/events and binaries, and retain every failure.
No dashboard C writes, old runtime reuse, hardware reset, gate waiver or driver
change. Actual Windows depth requires its own fixed pixels/module receipts.
