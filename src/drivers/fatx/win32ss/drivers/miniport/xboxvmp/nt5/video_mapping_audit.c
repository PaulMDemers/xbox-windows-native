/* SPDX-License-Identifier: GPL-2.0-or-later
 * Read-only CPU/mapping diagnostics for the pinned non-PAE NT5 build.
 * Does not change cache registers, page tables, display mode or pixels.
 */
#include <ntddk.h>
VOID NTAPI XwnVideoTrace(ULONG, ULONG, ULONG, ULONG);

static VOID TraceMsr(ULONG Number)
{
    ULONGLONG Value = __readmsr(Number);
    XwnVideoTrace(0x25, Number, (ULONG)Value, (ULONG)(Value >> 32));
}

static VOID TracePage(ULONG Tag, ULONG Address)
{
    volatile ULONG *Pde = (volatile ULONG *)(0xC0300000 + (Address >> 22) * 4);
    ULONG Directory = *Pde, Entry = 0;
    XwnVideoTrace(0x23, Tag, Address, Directory);
    /* Do not touch an absent page table or interpret a 4MiB PDE as a PTE. */
    if ((Directory & 1) && !(Directory & 0x80))
        Entry = *(volatile ULONG *)(0xC0000000 + (Address >> 12) * 4);
    XwnVideoTrace(0x24, Tag, Entry, (Directory & 0x80) ? 1 : 0);
}

VOID NTAPI XwnVideoTraceMapping(PVOID Virtual, ULONG Physical, ULONG Length, ULONG Ram)
{
    int Cpu[4];
    ULONG Features, Count, I, Cr4;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL) return;
    Cr4 = __readcr4();
    XwnVideoTrace(0x20, (ULONG_PTR)Virtual, Physical, Length);
    XwnVideoTrace(0x21, __readcr0(), __readcr3(), Cr4);
    __cpuid(Cpu, 1); Features = Cpu[3];
    XwnVideoTrace(0x22, Cpu[0], Features, Ram);
    if ((__readcr0() & 0x80000000) && !(Cr4 & 0x20) &&
        Length >= PAGE_SIZE && (ULONG_PTR)Virtual <= MAXULONG - Length &&
        (Ram == 0x03C00000 || Ram == 0x07C00000))
    {
        TracePage(0, (ULONG_PTR)Virtual);
        TracePage(1, (ULONG_PTR)Virtual + Length - PAGE_SIZE);
        TracePage(2, Ram + 0x80000000);
        TracePage(3, Ram + 0x80000000 + Length - PAGE_SIZE);
    }
    if (!(Features & (1 << 5))) return; /* RDMSR capability */
    if (Features & (1 << 16)) TraceMsr(0x277); /* PAT */
    if (Features & (1 << 12))
    {
        Count = (ULONG)__readmsr(0xFE) & 0xFF;
        TraceMsr(0xFE); TraceMsr(0x2FF);
        /* The owned PentiumIII target has eight variable ranges. Bound reads
         * for other advertised CPUs and leave truncation visible in MTRRCAP. */
        if (Count > 8) Count = 8;
        for (I = 0; I < Count; ++I)
        {
            TraceMsr(0x200 + I * 2);
            TraceMsr(0x201 + I * 2);
        }
    }
}
