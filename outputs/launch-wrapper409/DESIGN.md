# 409: isolate the pre-UI XBE allocation prefix

The physical407 menu/FTP attempts failed before observed Xromwell UI; a later
File Explorer boot of the same launcher reached Windows and Media Player.
408 verified the actual menu and launcher bytes. This does not prove that route
caused the failures; changing launch context or timing may expose intermittency.

The exact374 wrapper allocates a 1 MiB payload buffer, obtains its physical
address, copies the embedded payload, allocates a loader page and obtains an
identity virtual alias. Return values were unchecked in that wrapper. A new
diagnostic records those results; it neither fixes nor claims their failure.

Build003 uses the exact original wrapper/header/font and preserves the deployed
300624-byte image footprint, original embedded payload and padding, header
values, allocation arguments/order and original payload copy. Only the section
digest necessarily changes. Added instructions store flags/results and refuse
unsafe null-result or backward-copy paths. There are no extra kernel calls or
file opens until the allocation observation ends. The diagnostic stops BEFORE
the two relocated-loader copies, far-jump construction and paging transition.
It never enters Cromwell or Windows, changes video mode, or performs a GPU handoff.
Instrumentation changes instruction layout/timing and is not an unchanged boot.

The logger uses actual owned nxdk declarations/ordinals as ABI references, not
the nxdk startup/runtime. It creates one new report exclusively under a fixed
new E/Partition1 application directory, writes a 64-byte record, flushes, then
writes a 16-byte completion trailer, flushes/closes and calls HalRebootRoutine
(the same primitive as nxdk XReboot). A final flush failure cannot be inferred
from file bytes alone; exact subsequent readback establishes retained bytes.
Missing output does not prove no XBE entry: creation or later I/O could fail.
No C access, original launcher replacement, Startup change or Windows boot.

Host001/002/004 execute actual assembled x86 instructions in a 32-bit Linux
process, replacing the kernel thunk table with explicit memory/file models.
They cover 13 allocation, DF, existing-file, short-write and write/flush paths.
They are NOT emulator or physical qualification. Source buffers are checked
against the original payload. Independent decoders test actual model reports,
length/cookie/phase/range mutations and missing completion trailers.

Initial parser decode.py required the complete loader page below 32 MiB. The
actual call passes HighestAcceptableAddress=0x02000000, and physical001 returned
a page STARTING at that address. Original rejection/collection are immutable.
decode002.py explicitly accepts that observed inclusive start boundary (still
within 64 MiB RAM), rejects the next page, and records the exact address. This
is a corrected host assumption, not proof that the original handoff is safe or
that the address caused407. Kernel allocation success and completed handoff
remain separate questions.

Manual variant004 changes only two attempt-cookie dwords and one same-length
directory character plus the XBE section digest. Instructions/layout are exact
build003. A separate full source snapshot documents those substitutions. It
must be launched once through File Explorer, not via another FTP command.
The current protected files are checked before stage and after return. No old
attempt is repeated, and the original XWNEBoot file remains the working demo.
