# CPU register observation contract

Input EDI points to a caller-owned160-byte record, ECX equals160. Header is
C489/version1/size160/epoch1-or2/cookie48900101; body and trailer start zero.
Capacity is checked before the first destination dereference. Bad identity,
epoch, existing completion or trailer refuses without writes. The function
returns with all original general registers and EFLAGS. Completion is read from
the caller's record; an already-completed record is not permission to call again.
No reset API is supplied. External actor/slot ownership is an integration duty.

Offsets20..76 contain entry flags, four control registers, eight selectors,
GDTR/IDTR and call frame identity. TSC bounds occupy80..95. Offsets96..127 contain
the second control/table-register readings and reserved padding. State at132 and
DONE/cookie at152/156 identify completion. All holes must remain zero. Initial
and final control/table values must match for this decoder to accept a coherent
observed pair. This does NOT exclude changes and restoration between reads.
No interrupt disable, thread lock, serializing TSC barrier or atomicity is claimed.
TSC values are observations, not wall-clock deadlines or instruction timing proof.

Selectors alone do not establish segment bases/access rights. Descriptor-table
registers do not establish readable descriptor contents. CR3 alone does not
validate page tables or grant a safe physical-memory mirror. The decoder records
all these limitations explicitly. Mapping validation and a kernel-specific
bounded memory provider remain separate prerequisites for a page walker.

The test fixture alone sets synthetic CPU state, changes CR2/CR3 between epochs,
installs GDT/IDT and masks PIC interrupts. Those instructions are outside the
capture function and are NOT proposed Xbox adapter operations. The capture itself
uses only its destination and current call stack. Invalid capacity is tested with
an unmapped pointer to prove the early bound, not to claim arbitrary-pointer
validation for an otherwise valid capacity.

Build and run use separate owned resource leases. Exact488 pinned assembler,
linker, QEMU, BIOS, Multiboot loader and dynamic libraries are checked before use.
Source/test/decoder/reviewer are frozen before compilation. One new diskless VM,
no network or disk/EEPROM,15-second watchdog and bounded terminate/kill fallback;
any fallback or deadline fails. C reserve is64MiB build/128MiB run above20GiB.
Normal explicit test exit requires code33, exact packet, expected state, all
refusal/guard checks, and no CPU exception log. No physical access occurs.
