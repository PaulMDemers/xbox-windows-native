# 410: original copies and far-jump preparation, without paging transition

The two 409 physical probes returned identical successful allocation records.
Neither executed the later copies or handoff. This new diagnostic preserves the
original two 1024-byte copies (PAGE_SIZE / 4 with MOVSB, not 4096 bytes) and both
far-jump patches. The active loader/GDT span is 224 bytes, within that copy.
No claim follows that copying only 1024 bytes is a bug.

Before the original copies, refuse changed virtual alias, returned size other
than 4096, or a missing original +0x80000000 mirror identity. The original final
jump is replaced by bounded readback: original payload, both 1024-byte copies
with exactly the four-byte target fixup, and actual low-alias physical backing.
All kernel/file calls added for verification occur after original preparation.
The observer changes timing/layout; this is not an uninstrumented boot.

The low virtual page can have different physical backing from the contiguous
loader page. The original deliberately writes both so execution can cross the
paging transition. Different physical pages alone are not evidence of failure.
No CR0/CR3 changes, CLI, far jump, GDT load, Cromwell entry or Windows boot occurs.
The protected report lives outside the copied source span. File logger writes
128-byte header plus 16-byte trailer, then returns to dashboard using the same
primitive as 409. Missing/partial output is inconclusive; complete output does
not distinguish a final flush failure without retained readback.

Unique E:/Applications/XWNBoot410a, cookie41000101, exclusive report, one launch
and collection. Original launchers, Windows, C and rollback unchanged. Before/
after hashes cover the established 62 protected files, not full disk allocation.
No speculative patch is installed. Tests execute actual assembled x86 with
explicit modeled allocation, physical-address, file and reboot calls.

Build001/host001 failed before deployment: GAS encoded the reader's compound
symbol-displacement address as [esi], not [esi+74]. Build002 uses an explicit
index register for the read; source and disassembly reviewed. Original loader
copies/patch operations were unaffected. All failed inputs/output retained.
