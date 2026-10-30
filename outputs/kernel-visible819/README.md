# Kernel819 complete-mode recorder

Fresh kernel-context control of CLOSED native818. No native runtime reuse.
The full transaction is byte-for-source identical except its explicit framebuffer
pointer contract: the kernel high alias must equal physical|0x80000000 and every
owned framebuffer page plus the final byte is checked by MmGetPhysicalAddress.
The wrapper saves incoming flags, disables interrupts for the bounded transaction,
restores flags, then the caller writes phase/error and all40 raw result words.
It does not attempt to restore video through unqualified register writes. Failure
saves its result and requests firmware reboot; success holds its new720x480 pattern
15seconds and requests reboot. Neither is Windows normal shutdown.

Exact compiled object:165 modeled transaction/wrapper cases and32770 bounds;
2353 layout cases and26 compiled baseline admission cases. Protected-register,
wire, pixel and guard checks are host evidence only. Actual physical phase/error
is the experiment; native/Windows behavior remains unproved.

build001 failed because transaction.h includes a static delay helper unused by
main.c under Werror. Preserved private build/log and public failed receipt.
main.c scopes only that unused-function include diagnostic; build002 succeeded.
No candidate hardware mutation was changed to satisfy a test.

No hook; owned E application and reports only. One bounded SITE, no retry.
