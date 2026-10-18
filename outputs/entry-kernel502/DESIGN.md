# Early kernel file boundary502

Observe the exact499 XBE in a fresh xemu child of a never-executed preparation.
This is an emulator-only early file contract test, not a retry of physical501.
No physical console access, SDK changes, new XBE build or Windows startup.

At the actual early entry, compare all648 gate bytes and236 data bytes with the
reviewed binary. Retain the loaded header, registers, segments, GDT/IDT and actual
page-walk bytes. Match all eight resolved thunks to the live kernel export table;
BIOS pins do not constitute a full symbol-matched kernel image qualification.

Observe actual create,96-byte write,flush,16-byte write,flush,close entries and
returns. Check exact stdcall frames, native path/object/string and returned
status/IOSB/stack cleanup. Stop at the original start before it executes. Verify
state7 and restored registers/flags against the actual entry, and independently
decode the memory receipt. No host memory/register writes, API invocation,
status replacement, retry or Windows execution is permitted.

Failure leaves partial evidence and triggers bounded host cleanup. Remove all
owned breakpoints, restore physical-memory mode, then stop/quit the owned host.
The240-second outer watchdog remains active. The cold audit compares complete
virtual mapping and every child-local extent, FATX allocation ownership, exact
candidate and receipt, five hives, three baseline binaries, seed and EEPROM.
Host stop is not guest shutdown. Strict whole-disk equality remains a separate
gate even when expected receipt writes occur.

Host001 validates actual callsite extraction with synthetic frames. Host003
executes actual observer sequencing with kernel/memory/transport explicitly
modeled, including every transport failure boundary. Host002's invalid negative
changed one valid nonzero opaque handle to another; its failure and original
source are retained. Host003 uses zero for that invalid-handle test, with no
production change. Physical501 still supplied no early or Windows receipt.
