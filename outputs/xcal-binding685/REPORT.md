# 685 measured-rate native binding — host fixtures closed

The fresh host-only binding combines681's unchanged checked block protocol with
actual32-bit IN/OUT callbacks and an integer delay based on
[physical684](../video-clock684/RESULT.md). It is not integrated into Xromwell,
packaged as an XBE, or deployed to a console. Maintained default720p sources and
all release pins remain unchanged.

The delay uses1688 ticks (500.148us at the kernel-reported3.375MHz), a maximum
100,001 reads including the starting sample, and rejects backwards/large-gap
samples. It preserves full32-bit arithmetic, including rollover. The explicit
clock-qualified parameter is a caller precondition, not an automatic calibration.
The binding refuses all exported operations with IF set; it does not disable
interrupts itself. Native callers must establish exclusive bus ownership and
retain that context. No function clears unknown inherited pending status.

GCC12 sanitizer tests passed3,378 successful modeled step/wrap cases and the
stall/backwards/24-bit/gap/argument rejection checks. A fresh freestanding32-bit
image then passed33 isolated instruction-level fixtures in Unicorn:

- Correct block-read data and little-endian block-write bytes, exact port widths.
- Busy/dirty entry and IF-set refusal; failed reads leave caller output intact.
- Combined error flags, short block length, bounded read/write timeouts.
- Measured-rate delay, full32-bit rollover, frozen/backwards/24-bit clocks,
  excessive gaps and an unqualified clock.

These fixtures model port behavior. They prove neither physical block transfers
nor native timing/boot/display behavior. The copied681 header retains its original
host-prototype comment and exact bytes; `native.c` is the new experimental binding.
There is no positive chip-ID result or GPU programming in this work.

See [source pins](sources.json), [build](build001.json), [instruction fixtures](cpu001.json)
and [next steps](NEXT.md). All fixture invocations are closed; do not rerun them.
