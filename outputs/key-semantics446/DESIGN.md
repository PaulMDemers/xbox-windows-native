# RGB32 key comparison diagnostic

This new diagnostic isolates the failed rung04 operation. It does not alter
sprites.c, its expected pixels, or historical443/444/445 evidence.

Two bounded processes request default and software-only DirectDraw7 respectively.
Each uses an owned hidden window, NORMAL cooperative level, a16x12 RGB32 source
and32x24 RGB32 destination in system memory. There is no primary surface,
display-mode switch, runtime DLL replacement, Xbox deployment or GPU claim.

Twelve independent operations cross three keys (0,0xff0000,0x123456), plain/keyed
copy, and absent/two-rectangle clipper. The destination resets to0x335577 before
each copy. Source colors include exact keys and near-colors with equal low16
bits but different red bytes; spatial variation separates color from clip edges.
Each operation records actual Set/GetColorKey values, API results, lock layout,
source and destination. A mismatch increments the failure total but does not
prevent later independent operations. API/layout/I/O failures stop. Expected
full-width key comparison remains unchanged; a low16 comparison is a separate
explanatory model, never an acceptance rule or an attribution to instructions.

EnumDisplaySettings enumerates at most4096 records, requiring a terminating
false return before capacity. Current display and DirectDraw display reports
must agree. Unsupported modes are not requested or inferred from enumeration.
Raw captures contain12 consecutive frames of LE DWORD pixels:9216 source bytes
and36864 destination bytes per backend. Surface padding is not a guard claim.

The independent Python checker validates transport, required fields, mode bounds,
all operation receipts, cleanup, external process exit and independently computed
pixels. Complete diagnostic evidence can describe a semantic failure. It must
not be described as a passing rung04 result. Each guest process has a90-second
controller timeout; the owned emulator has a600-second outer watchdog.

The new launch adapter verifies the completed preflight itself immediately before
Popen. Exact preparation/cold receipts, fixture/parent/floppy hashes, runtime and
source dependencies, unique attempt identity and a one-hour validity window are
mandatory. Receipt publication uses a flushed temporary file plus exclusive
atomic hard link. Exclusive launch consumption precedes dispatch; a failed spawn
cannot retry that ID. The guard is an accidental-ordering/integrity check under
the cooperative lease, not protection from a malicious concurrent filesystem
writer. Host tests call this actual adapter with a modeled Popen.

The original build001 batch wrapper was copied before its receipt handling was
completed; it remains in the private build capsule. The current public wrapper
adds fresh-prefix checks and an external exit receipt. The guest controller
does not execute either batch wrapper: it launches the exact built executable,
waits for actual process exit and writes its own exclusive receipt.

Only a fresh child of closed404 is used. After normal guest restart, hash all
enumerated non-metadata file contents, check five hives and new shutdown events,
compare protected binaries, and independently read selected files through
read-only NTFS3G. Preserve failures and all sources. No full NTFS allocation
ownership or Xbox compatibility claim follows.
