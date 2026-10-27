# Xcalibur protocol review698

Source review and host-only prototype. No maintained launcher, driver, encoder
configuration or physical console was changed. Host001 is closed.

## Reading4 versus reading2

[SMBus block reads](https://docs.kernel.org/i2c/smbus-protocol.html#smbus-block-read)
return a count before their data. A byte-data transaction has the same command
and repeated-start prefix but terminates after its first response byte. Thus
686's byte-only4 is consistent with seeing the length of697's four-byte response,
whose payload was02 00 00 00. This is an inference, not a direct wire capture or
proof that both measurements had identical device state. No repeat is needed
merely to make those unlike values match.

Cromwell treats each Xcalibur address as four bytes. Its read helper discards
those bytes;681 and697 retain them. Register0's meaning is not established as a
silicon ID. Although raw2 agrees with byte order of the legacy table's first
word, that does not identify the active mode or validate the rest of the table.

## Status handling tightened in an isolated candidate

[Linux's nForce-capable AMD756 driver](https://github.com/torvalds/linux/blob/master/drivers/i2c/busses/i2c-amd756.c)
defines host active at bit3, bus active at bit11, and abort at bit0. The older
681/697 masks omitted host-active and abort. The new callback helper:

- Refuses either active flag or any known inherited terminal flag before writes.
- Samples full16-bit status; waits within its finite budget while still active,
  even if a completion flag is visible. Never acknowledges while active.
- Treats abort/collision/protocol/timeout as failure, even with completion.
- Reads exactly four FIFO bytes only after a non-busy, error-free completion and
  exact length4. Acknowledges only its own observed terminal bits.
- Publishes read output only after final known busy/terminal flags are clear.
- Retains entry/last/final status, length, count and acknowledgement. A late
  completion after the budget is recorded without acknowledgement or retry.

Both directions use block/start0d; address bit0 selects direction. This avoids
[Cromwell's legacy write helper](https://github.com/XboxDev/cromwell/blob/master/drivers/pci/i2cio.c)
extra control bit10. This choice follows the polled Linux sequence and still
needs physical write qualification. No IRQ/IF changes, abort/reset, inherited
status clearing or automatic retries are introduced. Poll counts bound calls,
not elapsed wall time. Unknown bits remain visible rather than being cleared.

GCC12 ASan/UBSan passed458,766 modeled cases: exhaustive16-bit entry, polled and
final status for both directions; every16-bit length; delay/last-read boundaries;
late completion; argument rejection; exact port widths/order/counts and unchanged
caller output on failure. These are callback models, not native controller proof.
The captured697 status10/final0 remains successful under the stricter predicates.

## Initialization boundary

The retained681480p sequence performs two reads and146 writes, with144 timed
pauses. The native timer has not yet been observed on694-697's minimal handoff.
[699](../native-timer699/REPORT.md) addresses that gap without SMBus activity.
The full BootStartup path remains separate from this checked minimal transition.

Before encoder writes, validate the complete GPU/output/clock/framebuffer
sequence and the strengthened helper in the actual linked native candidate,
including every failure exit. Then run a separate watched native480p pattern.
Windows1.6, native720p and acceleration remain unqualified. No firmware snapshot
or table from the running console is transplanted.

Reference snapshots and hashes: [references001](references001.json). Original
source licenses are retained; this helper is GPL-2.0-or-later. [Closure](closure001.json)
records source pins and scope. Earlier failures and closed tests stay immutable.
