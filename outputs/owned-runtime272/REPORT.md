#272 closed: actual standalone pixels match; strict disk gate fails

The reviewed271 build005 ran on the exact269 build005 renderer without an
observer operation or release helper. emu004 reached actual phases11,22,33.
Both180-pixel captures match the independent oracle:1440 unique framebuffer
bytes. Twelve source/guard reads total49152 exact bytes; the384-byte vertex
array also independently matches at each of the three stops. Guest error is0.
This establishes the owned guest pixel control, not four texture generations.

Actual loaded XBE headers/immutable section fields, four preload reference
counts, complete116224-byte text, checkpoint/caller/arguments and earlier record
state were checked. Runtime kernel base is0x80010000, image size636160, timestamp
1023192752, and the resolved physical-address function is export173. Kernel
resident bytes and PE/export identity were captured privately with firmware
hashes; this is not a symbol-matched Windows kernel or full kernel image pin.

Guest translations cover the four textures, vertices, stable framebuffer,
524288-byte pushbuffer plus8192-byte allocation allowance and conservative GPU
instance tail. Actual channel0 and context table were captured. Fifteen RAMHT
edges remain identical at all three stops. Full DMA/graphics object descriptors
were not all captured, and no host seven-family ledger/lifetime watch ran.
Neither guest idle polls nor RAMHT entries prove host completion or retirement.

emu004 started2026-10-11 23:58UTC and closed23:58:39UTC. All breakpoints were
removed and physical mode restored. Guest resumed through the pinned terminal
code's15second halt window; HAL entry itself was not traced. Host stop/quit
completed with exit0, no fallback kill. This standalone application never boots
Windows and has no Windows normal-restart/event/hive result.

The original strict whole-disk equality gate is FALSE. All three booted attempts
changed one byte in the reserved sector starting at1536; complete overlay
analysis covers65536 bytes and the entire8GiB mapping. All filesystem bytes are
inherited unchanged from the exact private base, whose first FATX partition is
at524288. Both QCOW checks are clean and EEPROM unchanged. The writer of that
reserved byte is not attributed or waived. This is separate from historical
Windows Ftdisk49 failures; there is no event suppression or revised PASS gate.

Independent review rehashed54 private captures and every frozen dependency.
The model rejected734 synthetic mutations; the revised actual-header checker
rejected224 byte mutations. The original inputs for each predecessor are
preserved byte-exact in prior001..003. No proprietary kernel bytes or images
are committed; private captures remain in E:/xwn272/emu004/private.

Preserved failures:
- emu001: Windows xemu could not open the Linux absolute QCOW backing path;
  launch failed before guest execution. Original8GiB disk/EEPROM remain exact.
- emu002: actual first checkpoint reached, then the host incorrectly compared
  mutable section reference counts against on-disk zero. Actual loader count1
  is recorded. Breakpoint teardown and orderly host exit0 completed.
- emu003: initial720 pixel bytes already exact, but a bounded backward kernel
  search continued below a containing PE into an unmapped page. The corrected
  search stops at the containing PE, then validates the actual import/export.
  Teardown and orderly host exit0 completed.

All four attempts are closed and must never be relaunched, recollected or used
as runtime parents. No physical access, SDK/renderer/native change, release,
performance measurement, acceleration or native Windows GPU ownership occurred.
Physical audio004/softwarevideo118/shared158/FATX0101 and recovery256 are intact.
