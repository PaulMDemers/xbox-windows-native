# Diagnostic receipt version 1 — host prototype only

The slot is exactly 1,536 bytes (three 512-byte sectors). No physical sector
address or filesystem path is embedded. The transport callback sees only slot
indices 0, 1 and 2. A future backend must independently establish ownership,
disk identity, allocation and bounds. This module does not authorize raw writes.

All integers are explicitly little-endian 32-bit values. No native struct
padding or pointer is serialized. CRC is IEEE CRC-32 (reflected polynomial
0xedb88320, initial/final XOR 0xffffffff); it detects accidental corruption,
not malicious substitution. The host must retain the expected nonzero 16-byte
attempt identity and nonzero 32-byte candidate SHA-256 independently.

## Payload (sectors 0 and 1)

| Byte offset | Bytes | Field |
|---|---:|---|
|0|8|ASCII XWN652R1|
|8|4|Format version, 1|
|12|4|Used payload length, 768|
|16|16|Unique attempt identity|
|32|32|Candidate executable SHA-256|
|64|4|Signed apply result (-1, 0 or 1)|
|68|4|Post snapshot point: 1 after return; 2 after original failure blanking|
|72|32|Request, eight words|
|104|36|State, nine words|
|140|252|Trace, 63 words|
|392|188|Pre snapshot, 47 words|
|580|188|Post snapshot, 47 words|
|768|256|Reserved, zero|

Request order: mode, ram, fb, reserved, hidden, encoder, cable, video_flags.
State order: stage, error, mutated, smb_attempts, smb_completed, sync_polls,
vblank_polls, vpll, pcrtc.

Trace begins waits_started, waits_completed, failed_wait, followed by six rows
of wanted, first, last, samples, byte_changes, bit_changes, completed, begin,
end, elapsed. No raw sample stream is claimed; these are the existing aggregate
observations from649. Each snapshot begins captured, cr_captured, index_before,
index_after, flags_before, flags_after, followed by the23 CRTC words and18 MMIO
words in651's captured order. Missing/partial captures retain their flags and
raw zero/value fields; no missing value is synthesized from a timing profile.

bridge.c assigns these named fields explicitly and has been tested against
the exact pinned651 native types. No wrapper hook is installed. Its caller must
stop updates to the source snapshots/trace while copying; this is not an atomic
cross-device snapshot.
The phase label is a producer claim, not something a checksum proves. The
decoder preserves raw measurements and does not infer hardware success from
their consistency or the apply result.

## Commit sector (sector 2)

| Byte offset within sector | Bytes | Field |
|---|---:|---|
|0|8|ASCII XWN652C1|
|8|4|Version 1|
|12|4|Payload length 1024|
|16|16|Same attempt identity|
|32|32|Same candidate SHA-256|
|64|4|CRC of both complete payload sectors|
|68|440|Reserved, zero|
|508|4|CRC of the preceding508 commit bytes|

The seed for each sector has ASCII XWN652S1, version1 at8, that sector's index
at12, attempt at16 and candidate digest at32; bytes64..507 are zero and the last
four bytes contain its CRC. Before any write, all three sectors must match
their entire expected seed, not just magic or a checksum. A used or torn slot
is not repaired or reset. A new attempt requires a separately owned fresh slot.

## Protocol and uncertainty

The successful callback sequence is `RRRWWFRRWFRRR`: read three seeds; write
two payload sectors; flush; read and compare payload; write commit; flush;
read and compare all three sectors. At most eight reads, three writes and two
flushes. The in-memory one-shot guard is consumed before the first callback.
Every callback error stops immediately, including an uncertain completion.
There is no retry and no metadata, FAT, directory or allocation operation.

A commit can be visible even when its flush or final readback failed. A valid
record is therefore not evidence that the producer observed successful flush
completion. Independent post-return collection must retain both the bytes and
any available producer status, preserving uncertainty. Actual device durability
and reset behavior are outside the callback model. The implementation bounds
callback counts, not wall time: a backend that hangs can still hang the caller.

The caller owns a2,048-byte scratch structure, plus the function uses a512-byte
temporary seed. Inputs, scratch and guard must occupy separate valid memory;
this is a single-threaded, non-reentrant API. No allocation, hardware I/O,
interrupt manipulation or timer access exists in the module itself.
