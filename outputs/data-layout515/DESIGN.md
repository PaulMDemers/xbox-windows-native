# A data-address experiment, not a paging fix

Keep exact510 code addresses and behavior, the five-byte11100 trampoline,
import table, executable section flags/extents and final image length. Relink the
320-byte data block at94c20 and change only its actual relocations. Preserve the
old95000 block as unreachable retained bytes so removing a page or shrinking the
image cannot become another variable. Do not change mappings, cache policy,
interrupt state, kernel API contracts, one-shot behavior or failure handling.

The next candidate needs a fresh namespace. Update the four inherited lower
path strings and the active relocated entry path, retaining the unused old510
data tail literally. This namespace difference is explicit and independently
normalizable, not grounds for retrying an unchanged closed runtime. Original
GPL wrapper licensing remains; new review code is MIT.

Two independent computations are used here: ELF32 REL arithmetic reconstructs
the full retained link and generates the proposed sections; an inverse checker
uses the original pointer ledger to restore and compare every byte of the pinned
original. GNU objdump independently decodes the original and proposed diagnostic
fragments. A byte scan independently closes the static old-data-pointer inventory.
All future candidate bytes must be reviewed again, including the new namespace.
This review does not execute code and cannot certify dynamic memory ownership,
kernel availability, stack viability, physical mapping or successful file I/O.

Entry first saves flags/GPRs on the inherited stack, clears DF, and accesses the
one-shot data state before SMBus. Relocation isolates that data address; failure
could still be earlier stack/code dispatch or later API behavior. Historical494
and emulator513 evidence must remain distinguished from a future physical run.
The optional user's LED observation may narrow this without a new boot.

No usable XBE is produced by this review. The synthetic full image stays in
memory; its hash is recorded only for reproducibility. The saved private929-byte
fragment has no header/import environment and is used only as disassembler input.
