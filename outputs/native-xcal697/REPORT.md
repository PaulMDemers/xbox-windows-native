# 697 launched; user reports GREEN hold; raw-word photo pending

One SITE accepted2026-10-27T02:26:54.767389Z after contextual user confirmation.
User reports "Green holding" in response to handoff/result-bar question. This
supports the reviewed4-byte response/pure completion/final known-flags-clear
success indication. Raw data word/status/length have not been optically captured.
Keep the console holding for a photo of all ten bit rows before requesting reset.
No repeat launch or collection yet. No hook, Windows or encoder configuration.

Native RAM is lost on reset; files contain pre-transfer preparation only. After
photo/observation, request manual power-cycle and await dashboard confirmation,
then collect697 once. No owned host process; hardware ticket retained, automation
paused. Read697/NEXT.md. Do not infer a unique encoder ID or native initialization.

# Native Xcalibur read697: built, validated and staged

This diagnostic attempts one native block read at address70/register00 after the
checked paging transition. It does not write encoder configuration or initialize
video. It accepts raw data only when the reported length is exactly4, completion
has no error, and final busy/terminal flags are clear. The raw value is not treated
as a unique encoder ID. Current watch/reset availability has been requested.

Kernel platform, framebuffer and allocation admission are unchanged from696 after
namespace renaming, as is the transition through the independent green header.
This includes current HDMI/NTSC/720p/64MiB eligibility, actual framebuffer checks,
separate physical/virtual reservation custody and matching4096-byte page copies.
Native CPU context and PCI identity/I/O-enable/BAR gates remain. The probe does
not independently reread cable/EEPROM in native context; it retains the current
kernel admission and performs no encoder mode/configuration write.

The controller command is C004=E1 (8-bit read address), C008=00 (8-bit register),
C002=0D (8-bit block-read start). Entry busy0800 or terminal0036 refuses before
command writes. At most100,000 status-byte polls occur. Done+error is failure;
only pure done reads the16-bit length atC006. A wrong length causes no FIFO read.
Exactly four bytes are read fromC009 for length4 and packed low byte first.
Only owned observed terminal bits0036 are acknowledged, once. The final16-bit
status is retained; busy/terminal flags reject. Timeout never acknowledges,
resets or retries, even when a late completion appears in the final sample.
This bounds software polls, not hardware I/O-cycle or kernel API wall time.

Protocol provenance is the pinned authored689/xcal_bus.c in review001.json.
Assembly remains GPL-2.0-or-later; supporting source licenses are unchanged.
The native code occupies1143 bytes before GDT4c0; descriptor pointers end4f6,
input500, native context540, final shadow580..5a0, IO data5a0..5cc, IDT600..e00,
stacke00..1000. Native result records are RAM/display only. The persisted CPU
sample remains pre-file-write and cannot stand in for native context after reset.

## Validation

- Build001/extract001 pin the actual linked template. Forty actual-linked IO
  models pass, including zero/short/oversized lengths, varied32-bit payloads,
  timeout, last-poll success, inherited status, bus errors and final dirty status.
  Port order/counts, forbidden FIFO reads, acknowledgement ownership, stack,
  full-frame pixels and memory guards are checked independently.
- Ten fresh diskless CPU fixtures pass. Three mappings execute the full transition
  and actual PC PCI refusal; seven malformed/fault cases stop without display
  changes. All ten VMs are closed. They do not emulate an Xbox transaction.
- Nine nxdk-object page-builder and nineteen allocation-policy cases pass.
  These models do not establish physical bus success or native initialization.

Staging exact readback passed at `E:\Applications\XWNNative697\default.xbe`.
XBE SHA-256: `9f3dccb49ed4d218ac675f98d94b3639e1f604adf2f768638e4acda1aaa162f7`.
No startup hook, Windows payload, dashboard C access or ordinary launcher change.
There is no697 build/model failure so far; all earlier696/695 failures remain.

## Display and interpretation

The first bar is the independent green handoff checkpoint. The second settles
to green=protocol success, red=PCI identity, cyan=I/O disabled, yellow=BAR,
orange=inherited busy, magenta=inherited terminal, blue=timeout,
red-orange=bus error, white=dirty final status, violet=length not4.
Ten MSB-left rows show ID, command/status, BAR, entry, last poll, raw word, final
status, result code, poll count and returned length. White=1, black=0; unread
values use FFFFFFFF. Successful native execution deliberately holds for reset.

Read the latest NEXT.md and launch/observation/collection records for current
physical state. Host success and a staged executable are not a physical result.

## Physical result and closure

One accepted launch produced held green handoff/result bars. Ten MSB-left rows:

| Field | Optical value |
| --- | --- |
| PCI ID | 01b410de |
| PCI command/status | 00b00001 |
| BAR | 0000c001 |
| Entry status | 00000000 |
| Last poll | 00000010 |
| Raw assembled word | 00000002 |
| Final status | 00000000 |
| Result | 00000001 |
| Poll count | 0000017f (383) |
| Block length | 00000004 |

The bounded native transaction received four bytes02 00 00 00 with pure
completion and final known flags clear. This does not establish a unique ID or
initialize the encoder. Earlier kernel byte-read4 is a different transaction;
establish comparability before drawing a conclusion from different values.

photo001 rejected calibration extrapolated from the left half. photo002 uses
local component spacing and fits all isolated components, then samples all320
cells at three thresholds and five offsets. White cells merge with the white
quadrant. photo-review001 independently uses adjacent-row geometry for rows1..8;
all256 bits agree. This is optical evidence, not a register dump. Photo private.

After user-confirmed manual power-cycle, collection001 read eight preparation
records twice. closure001 verifies private hashes and frozen source pins; staged
XBE/owner and unrelated entries unchanged. No hook existed. Runtime697 closed;
no repeat/recollection. Saved CPU is pre-file-write; native context is lost on
reset. No Windows shutdown or Windows1.6 support claim. Closure also preserves
two host documentation-script failures (report-key assumption and UTF-8 decode).
