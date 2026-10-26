# 687 bounded configuration reader and compiled handoff comparison

This host-only candidate adds a small native reader for the SMC cable byte and
EEPROM video settings. It prepares a separate Xcalibur path without changing the
maintained launcher or its Conexant behavior. No XBE was built or deployed for687.

The allowlist is seven-bit SMC address `0x10`, register4, and EEPROM address
`0x54`, registers `0x58..0x5b` and `0x96`. These cover cable, video standard and
the relevant video flags, without reading keys or serial numbers. The pinned
Cromwell `BootEEPROM.h` defines the standard at `0x58..0x5b`; the existing
`DetectVideoStd` reads `0x5a`. Config decoding/admission is not implemented here.

The reader refuses a busy controller or inherited terminal status before any
output. It starts a byte-read command, polls at most100,000 times, gives error
bits priority over completion, acknowledges only its own terminal result, and
leaves caller output intact on failure. A poll count is not a wall-time bound.
The native wrapper refuses IF-set entry and never changes IF. Exclusive bus
ownership remains a caller obligation. The copied685 block and delay code is
unchanged; its clock-qualified argument remains an explicit precondition.

## Integration finding

The legacy `ReadfromSMBus` acknowledges old status before starting a transaction,
but returns after a successful read without acknowledging that completion.
`BootResetAction` calls the legacy full EEPROM reader before video initialization.
Consequently, simply attaching the new strict reader afterward can encounter
inherited completion status and correctly refuse it.

Two fresh instruction-level sequences used the retained677 compiled image and
the new687 compiled image with an explicit write-one-to-clear status model:

- Legacy byte read succeeded and left status `0x10`; the checked reader returned
  dirty-status failure after one input, with no output or caller-value change.
- Two checked configuration reads followed by a checked block read succeeded;
  each acknowledged its own completion and left modeled status zero.

This establishes compiled behavior under that model. It is not an observation
of the physical native handoff, and does not justify clearing unknown status.
The proposed separate pattern path should enter before legacy EEPROM/encoder
transactions and establish its actual context there.

## Validation and closure

GCC12 sanitizer delay checks passed3,378 modeled successes plus rejection cases.
A fresh freestanding32-bit image passed48 port/delay/configuration fixtures,
including all six allowed register reads, refused addresses/registers, IF,
busy/dirty status, combined errors and the bounded timeout. The two sequence
fixtures above also passed. All invoked fixtures are closed; do not rerun them.

See [source ancestry](sources.json), [build](build001.json),
[48 instruction fixtures](cpu001.json), [sequences](handoff001.json),
[post-run pin review](review001.json), and [closure](closure001.json).
The sequence's legacy image matches677's retained wrapper receipt; the new
image matches687 build and instruction-test receipts. No maintained source,
manifest, ordinary startup or console file was changed by687. All owned host
commands exited; no VM or persistent process was started.

No native hardware block transfer, encoder programming, Windows boot, native720p
or acceleration is qualified. [686](../encoder686/REPORT.md) is a separate
kernel-service presence observation. Continue with [NEXT](NEXT.md).
