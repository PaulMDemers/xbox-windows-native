#715: read-only common-setup register capture

714's watched GREEN supports a specific CR19 changed readback and restoration.
Before extending writes to704's other common setup,715 captures all11 PRAMDAC
setup registers. The kernel saves two ordered read passes in preparation files;
native code independently repeats the reads and renders its first pass and a
second-pass mismatch mask. No native blank, unlock, CR19, encoder, timing, clock,
interrupt or other GPU-data writes occur. Indexed selector access from the inherited
baseline check is saved/restored. Framebuffer diagnostic drawing is explicit.

## Optical schema and interpretation

The second bar is GREEN for stable reads0x715, ORANGE for mismatch0x7152; other
bridge-refusal colors remain. Stable does not mean the values match the kernel.
A full-screen photo is required to compare native values with kernel files.
Thirteen bit rows appear on a gray panel. Each has32 bits, MSB at left, white1,
black0. Row0 is signature7150000b; row1 is the11-bit mismatch mask. Rows2..12:

| Row | GPU offset |
| --- | --- |
| 2 | 0x680884 |
| 3 | 0x680888 |
| 4 | 0x68088c |
| 5 | 0x680890 |
| 6 | 0x680894 |
| 7 | 0x680898 |
| 8 | 0x68089c |
| 9 | 0x680880 |
| 10 | 0x680630 |
| 11 | 0x68084c |
| 12 | 0x6808c4 |

Coordinates at1280x720: gray x112..1167/y104..639; each20x20 bit begins at
x128+32*bit,y120+40*row. The native result is exactly256 bytes; first52 words
retain the earlier struct layout but unused observations remain zero. Setup values
are words52..62, mismatch word63. Signature/mask must decode before interpreting
values; glare/ambiguous bits remain unknown. No prior firmware values are substituted.

## Validation and preserved failure

payload001 failed compilation because the inherited wait715 helper became unused.
The full source snapshots, receipt and private failed build remain; failure001
records them. payload002 omits the unused include and passes. No console was
accessed for that failure. Raw5176-byte payload is padded to9916. Seventeen ELF
relocations include six internal absolute32 entries; all page builders now require
six, with independently exercised rejection/relocation checks.

Fresh131379 ownership cases, four ASan/UBSan page placements,12 diskless CPU cases
(all closed),148 relocated instruction models,25 compiled nxdk page cases and372
compiled ownership cases pass. Models forbid native GPU-data and output-gate writes,
require exactly two ordered11-register capture passes, test each mismatch bit and
combined mismatch, and compare every framebuffer byte against an independent
binary-string optical oracle. Source and linked payload/bridge hashes are pinned.
Kernel capture code separately records both read passes; native optical comparison
still requires physical evidence. Current xemu lacks many selected PRAMDAC reads,
so zero from that emulator is not a hardware reference (source-review001).

## Physical lifecycle and limits

Unique owned E staging/readback; one accepted launch at most. The picture holds
for observation/photo and manual power-cycle. No Windows, startup hook or console
C access. Reports persist preparation only, not native results. Kernel versus
native equality, physical stability and native mode setup remain unqualified
until actual evidence arrives. Reading these registers does not validate writing
them, using firmware state as a replacement mode table, or Windows1.6 support.

One SITE accepted2026-10-27T06:33:51.629403+00:00. User reported GREEN holding.
Photo decoded, manual reset confirmed and collection completed; see closeout.
No repeat launch.

## Closed physical result

GREEN holding was followed by the complete user photo. All416 bits decode cleanly
under three thresholds and five sampling offsets;352 middle-row bits also agree
using adjacent-row geometry. Signature7150000b and zero mismatch are verified.
The original photo remains private; photo001 records its hash and samples.

After confirmed manual power-cycle, nine preparation files collected once and
passed source/binary/report, independent-alias, allocation and unrelated-entry
audits. PCI/CRTC/SEQ/geometry/allocation match714. All11 optical native values
match BOTH kernel passes, which also report zero mismatch. In the listed order:

`00000000 00000000 10001000 10000000 10000000 10000000 10000000 21101100 00000003 00801080 40801080`

Only offset680630 differs from704's11-value common PRAMDAC target: actual3 versus
target2. This narrows a concrete difference, not the cause of708/709's black screen.
It also does not cover704's six common CRTC writes, later geometry or encoder.
Native values are optical evidence; files are kernel preparation, not native dumps.

715 is CLOSED; console at dashboard, no hook or host process. Manual reset is not
normal Windows shutdown. Next review680630 semantics and prepare a separate bounded
single-register test/restore with observability before any launch. Do not patch
functional mode code, borrow firmware values or retry the full failed transaction.
