# Earliest-entry receipt: a positive witness, not a boot repair

497 is closed. Its SITE reply was acceptance, all 84 observations found dashboard
FTP, and none of the four launcher receipts or Windows results appeared. The first
existing receipt is written after preparation. Source and binary comparison shows
only four path literals/section hash differ from the earlier 494 launcher. No
functional paging, allocation, driver or interrupt change follows from that.

The proposed entry.S gate runs before the old entry code. It saves EFLAGS and all
general registers on the existing stack before touching them, clears DF locally,
and records the original registers, stack pointer and segment selectors. On full
I/O success it restores registers/EFLAGS and jumps to the unmodified old entry.
The old code will therefore still see and refuse an originally set DF. The gate
has no control-register, descriptor-table, segment-register, port or MSR writes.
Its static record/state is one-shot. A repeated entry refuses without rewriting
the first record or retrying file operations. Failure never continues preparation.

The owned path is a fresh E:\Applications\XWNBoot498a\entry.bin (native partition1).
Create is exclusive, synchronous/nonalert, write-through and non-directory, using
the same pinned Xbox thunk contracts as 497. Six calls on success: create, write
96-byte body, flush, write 16-byte trailer, flush, close. Strict zero status and
IOSB/byte-count checks refuse pending, stale IOSB and short results. Close is tried
at most once for a handle obtained from a successful create; its attempted flag
is set before calling. Failure snapshots stage/status/IOSB before cleanup. No
fallback file, retry, allocation, rearm or refcount assignment exists.

The trailer includes FNV-1a over all 96 body bytes, cookie and length. This detects
accidental corruption; it is not authentication. Independent decode requires exact
extent, schema, reserved fields, selector widths and checksum. A complete file is
only an entry witness: the final flush or close can fail after those bytes exist.
The decoder deliberately never claims close, preparation, Windows or graphics PASS.
Fresh staging, actual provenance, cold readback and later receipts remain required.
An ABSENT file still cannot exclude file-I/O failure or prove that entry was never
reached. The pending user's screen observation remains independent evidence.

The call count is bounded; individual Xbox kernel calls have no cancellation or
deadline guarantee. STATUS_PENDING is a refusal, not proof that an outstanding
operation completed. Static metadata/buffers are never freed. The firmware-return
call on refusal follows the existing diagnostic convention; its completion is not
host-proved. An unexpected return traps with UD2. A console observation deadline
must report a still-running/hung console rather than claim teardown.

host001 executes the actual proposed assembly as Linux i386 machine code. Only
the Xbox NT file/firmware services are modeled. 128 flag combinations check every
general register, ESP and flags on success; 71 failures/cleanup variants test
actual control flow, stdcall argument layout, DF clearing, exclusive-create flags,
byte counts, no retry/duplicate close, no continuation and immutable reentry.
The test does NOT cover ring0 interrupt/control state or actual Xbox filesystem
behavior. No ASan/UBSan, CPU-emulation, physical or ordinary-boot claim is made.

Before an actual candidate, prefer changing the XBE entry-address field to an
appended gate whose success target is the old _start. That can preserve every
original instruction and its address. Independently validate image/section extents,
all five unique paths, thunks, header hash, payload and original privileged body.
Use a NEW build/controller ID and full prebuild dependency pins. The current host
tool hashes were collected after compilation, not a full prebuild compiler closure.
No XBE integration, deployment or launch has occurred in 498.

Early I/O changes timing, kernel memory usage and cache state before preparation.
Even a successful candidate is a diagnostic intervention, not a boot-stability fix.
Ordinary launcher/startup, 720p, dashboard C, immutable releases and prior failures
remain protected. No new Windows startup hook is needed just to prove entry.
