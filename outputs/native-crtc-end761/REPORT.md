# Test761 preparation: native CR01 display-end checkpoint

Source-only extension of closed kernel760 and native759. No closed runtime is
reused. The new operation captures its own CR01 byte, writes `(720 / 8) - 1`
(`59`), checks six neighboring bytes, and restores the saved CR01 byte before
reversing the earlier operations. No later CR02 write or CR17 enable is added.
The ordinary Windows launcher and protected720p configuration are unchanged.

The result structure is176words/704bytes, located at page offset5100..53c0.
The existing initialized extent ends5400; the guard is5400..6000 and the
stack6000..8000. Native CPU admission remains paging off, CR3zero, interrupts
disabled, non-PAE and the existing cache-state predicate. There are no added
control-register writes, CR1b/CR22/CR33 data writes or borrowed firmware state.

The13-row optical report exposes signature, finalcode, eight aggregate recovery
masks and CR01 before/after/restored. The second CR05 recovery mask is omitted
from the picture to fit CR01's complete triplet. It is still checked by the
payload and required for final761. A green final status is therefore the
program's combined result, not a direct observation of that omitted mask.
Forward status, CPU registers, selectors, neighbor readbacks and prior
individual restoration values are also unexposed. See optical-schema001.json.

Host validation is preparation evidence, not physical timing, caching or mode
proof. This native probe deliberately holds, requires a photographed report and
manual reset, and cannot write a post-native disk result. Pre-handoff preparation
files will be collected only after the photo and reset. A manual reset is not a
normal Windows shutdown. Complete1.6 mode switching and Windows remain unqualified.

Preserve kernel760/model001's decimal/hex fault-injection mistake;761 starts
from corrected model002. Fault names c23-after-c1-read and c1-c23-coupling mean
CR17 (decimal23). No prior failure is superseded by this preparation.

Fresh preparation checks passed189 ELF cases,12 diskless CPU fixtures (all
closed),179 relocated execution cases,76 whole-framebuffer optical cases,
32 compiled page-builder cases and372 compiled ownership-plan cases. Source
comparison, initialized bounds, relocation and PE/XBE linked-byte checks passed.
Frozen source and Git index bytes match. The unique E/Applications/XWNMode761
package was staged and read back exactly; no startup hook or console C access.
XBE SHA256 ed4ab5772f241fddcf48e558b9753f8e7b21af7986b0ba4497884eb03e6e6c24,
131072bytes. No launch yet. Current watcher/photo/reset readiness is required.
