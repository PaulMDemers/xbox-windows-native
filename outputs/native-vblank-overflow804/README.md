# Native804: CR07 vertical-blank-start overflow

Source-only successor to CLOSED801 and CLOSED803. Kernel803 observed CR07
`36 -> 3E -> 36`, eight unchanged neighbor triples, and all29 recovery masks
clear. This native attempt adds that transaction after CR09 and restores its
own saved CR07 before unwinding CR09 and the earlier setup. It does not write
CR1b, CR22 or CR33 and does not claim a complete mode change or Windows boot.

The first native sizing measurement exceeded the previous payload allocation:
25912 bytes original, 24088 with compact sentinel initialization. A separate
no-unwind measurement was23928 and is not selected. Sharing only the CRTC
read/write helper bodies (`noinline`) reduced the selected payload to22592
bytes. Original and selected compiled ELF executions match exactly across894
cases for register/port traces and all700 result words. Timing equivalence is
not claimed. `measure001.json` and `measure002.json` retain all measured alternatives;
`size-decision001.json` records the initial size rejection.

The owned allocation remains32768 bytes. The selected payload occupies22656
bytes including64 bytes of padding. Request6880..68BC, guard68BC..68C0,
result68C0..73B0, guard73B0..7500, IDT7500..7D00, and stack7D00..8000
are disjoint (offsets hexadecimal). The existing768-byte stack is retained.
Full-bridge tests independently check actual stack writes and every report pixel.

Active source and build chain:

- `payload_build008.py`: selected `probe-shared-native.c`, transaction804.c.
- `host_build009.py`: bridge003.S, page002.c, plan.c; four fresh layouts.
- `model001.py` / `model002.py`: original/selected actual ELF fault execution.
- `integration012.py`: complete relocated bridge,700-word result and framebuffer.
- `cpu005.py`:12 fresh diskless CPU fixtures, each closed after observation.
- `build012.py`: nxdk frontend with exact tested payload and bridge embedded.
- `source_review001.py` / `review_prepare001.py`: independent source/layout
  reconstruction and exact frozen admission manifest.
- `physical008.py`: unique E path, readback, one20-second SITE request; no hook.

Measurements and host models are not physical device semantics or timing proof.
No Windows/game/media/firmware binaries are stored in this public kit. Full
numeric diagnostic receipts are losslessly encoded; `restore_receipts001.py`
verifies their hashes without re-executing any closed runtime.
