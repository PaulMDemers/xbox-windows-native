/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

#ifdef XBOX_NT5_MAP_PREFLIGHT
extern const UCHAR XwnMapFont[4096];
VOID HalpXwnMapEntry(VOID);
static volatile ULONG XwnMapRecord[96] = {0x564e5758,0x35544e50,1,0};
static PULONG XwnMapSeed;
static PUCHAR XwnMapTarget;
static UCHAR XwnMapOriginal[5];
static BOOLEAN XwnMapReady;

static BOOLEAN HalpXwnDisplayMapped(VOID)
{
    ULONG Address, End = XwnMapRecord[20] + XwnMapRecord[21];
    for (Address = XwnMapRecord[20]; Address < End; Address += PAGE_SIZE)
    {
        ULONG Va = Address + 0x80000000;
        volatile ULONG *Directory = (volatile ULONG *)0xc0300000;
        volatile ULONG *Pte = (volatile ULONG *)(0xc0000000 + (Va >> 12) * 4);
        if (!(Directory[Va >> 22] & 1) || (*Pte & 0xfffff01b) != (Address | 0x1b))
            return FALSE;
    }
    return TRUE;
}

static VOID HalpXwnMapText(ULONG Row, PCSTR Text, ULONG Color)
{
    ULONG Ch, X, Y, Pitch = XwnMapRecord[19] / 4;
    volatile ULONG *Pixels = (volatile ULONG *)(XwnMapRecord[20] + 0x80000000);
    for (Ch = 0; Text[Ch] && Ch < (XwnMapRecord[17] / 8) - 6; ++Ch)
        for (Y = 0; Y < 16; ++Y)
            for (X = 0; X < 8; ++X)
                Pixels[(Row*16+Y)*Pitch+(Ch+3)*8+X] =
                    (XwnMapFont[(UCHAR)Text[Ch]*16+Y] & (0x80>>X)) ? Color : 0xff000000;
}

static VOID HalpXwnMapHex(ULONG Row, PCSTR Label, ULONG Value)
{
    CHAR Text[80]; ULONG I = 0, N;
    while (Label[I] && I < 64) { Text[I] = Label[I]; ++I; }
    for (N = 0; N < 8; ++N) Text[I++] = "0123456789abcdef"[(Value >> (28-N*4)) & 15];
    Text[I] = 0;
    HalpXwnMapText(Row, Text, 0xffffffff);
}

/* Called by an assembly jump target, with the original MiInitMachineDependent EBP. */
DECLSPEC_NORETURN VOID NTAPI HalpXwnMapCheckpoint(PULONG Frame)
{
    ULONG Cr0 = __readcr0(), Cr4 = __readcr4(), I, Absent = 0;
    BOOLEAN Valid;
    volatile ULONG *Directory = (volatile ULONG *)0xc0300000;
    XwnMapRecord[86] = __readeflags();
    _disable();
    Valid = XwnMapReady && XwnMapRecord[3] == 30 && XwnMapRecord[24] == 80 &&
            (ULONG_PTR)Frame >= 0x80000000 && Frame[2] == XwnMapRecord[4] &&
            Frame[1] == XwnMapRecord[6] + 0x155b55 &&
            (Cr0 & 0x80000000) && __readcr3() == XwnMapRecord[11];
    for (I = 0; I < 512; ++I) if (!(Directory[I] & 1)) ++Absent;
    XwnMapRecord[90] = Absent;
    Valid = Valid && Absent == 512;
    /* Flush global and non-global translations. A cached low translation
     * must not accidentally keep the old loader display alive. */
    if (Cr4 & 0x80) __writecr4(Cr4 & ~0x80);
    __writecr3(__readcr3());
    if (Cr4 & 0x80) __writecr4(Cr4);
    XwnMapRecord[91] = 1;
    __writecr0(Cr0 & ~0x10000);
    RtlCopyMemory(XwnMapTarget, XwnMapOriginal, 5);
    __writecr0(Cr0);
    XwnMapRecord[87] = memcmp(XwnMapTarget, XwnMapOriginal, 5) == 0;
    XwnMapRecord[81] = 0;
    XwnMapRecord[82] = Frame[2];
    XwnMapRecord[83] = Frame[1];
    XwnMapRecord[84] = Cr0;
    XwnMapRecord[85] = __readcr3();
    XwnMapRecord[89] = (ULONG_PTR)Frame;
    XwnMapRecord[92] = XwnMapRecord[20] + 0x80000000;
    XwnMapRecord[93] = HalpXwnDisplayMapped();
    XwnMapRecord[94] = (ULONG_PTR)HalpXwnMapCheckpoint;
    XwnMapRecord[95] = (ULONG_PTR)XwnMapRecord;
    Valid = Valid && XwnMapRecord[87] && XwnMapRecord[93];
    XwnMapRecord[24] = 100;
    XwnMapRecord[3] = Valid ? 90 : 40;
    if (XwnMapRecord[93])
    {
        volatile ULONG *Pixels = (volatile ULONG *)XwnMapRecord[92];
        for (I = 0; I < XwnMapRecord[21] / 4; ++I) Pixels[I] = 0xff000000;
        HalpXwnMapText(4, "XWN Windows 2000 low-mapping transition", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNV90: Low mappings cleared; high HAL display active."
                             : "XWNVFAIL: Mapping checkpoint validation failed.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Absent low PDEs: ", Absent);
        HalpXwnMapHex(12, "CR3: ", XwnMapRecord[85]);
        HalpXwnMapHex(14, "Framebuffer VA: ", XwnMapRecord[92]);
        HalpXwnMapText(17, "TLB flushed; original kernel bytes restored.", 0xffffffff);
        HalpXwnMapText(19, "Stopped BEFORE RAM descriptor scan and storage.", 0xffffffff);
        HalpXwnMapText(22, "Photograph this screen, then reboot to dashboard.", 0xffffffff);
    }
    for (;;) __halt();
}

ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
    static const UCHAR Expected[8] = {0x8b,0x45,0x08,0x33,0xdb,0x8d,0x48,0x08};
    PIMAGE_NT_HEADERS Nt;
    ULONG Cr0;
    if (!Seed || Signature != 0x4d504e54 || XwnMapSeed || Seed[6] < 0x80000000 ||
        Seed[7] != 1691648 || Seed[11] != __readcr3() || Seed[20] < 0x03c00000 ||
        !((Seed[17]==640 && Seed[18]==480 && Seed[19]==2560) ||
          (Seed[17]==1024 && Seed[18]==576 && Seed[19]==4096)) ||
        Seed[21] != Seed[18]*Seed[19] || Seed[20] > 0x04000000-Seed[21]) return 0;
    Nt = (PIMAGE_NT_HEADERS)(Seed[6] + ((PIMAGE_DOS_HEADER)Seed[6])->e_lfanew);
    if (Nt->Signature != IMAGE_NT_SIGNATURE || Nt->FileHeader.TimeDateStamp != 1266293717 ||
        Nt->OptionalHeader.CheckSum != 1747402 || Nt->OptionalHeader.AddressOfEntryPoint != 44560 ||
        memcmp((PVOID)(Seed[6]+0x157f3e), Expected, sizeof(Expected))) return 0;
    RtlCopyMemory((PVOID)XwnMapRecord, Seed, 96*sizeof(ULONG));
    XwnMapRecord[0] = 0x564e5758;
    if (!HalpXwnDisplayMapped()) { XwnMapRecord[3] = 0; return 0; }
    XwnMapTarget = (PUCHAR)(Seed[6]+0x157f3e);
    RtlCopyMemory(XwnMapOriginal, XwnMapTarget, 5);
    Cr0 = __readcr0(); _disable(); __writecr0(Cr0 & ~0x10000);
    XwnMapTarget[0] = 0xe9;
    *(PULONG)(XwnMapTarget+1) = (ULONG_PTR)HalpXwnMapEntry-(ULONG_PTR)(XwnMapTarget+5);
    __writecr0(Cr0);
    Seed[80] = (ULONG_PTR)XwnMapTarget;
    Seed[88] = (ULONG_PTR)HalpXwnMapEntry;
    XwnMapSeed = Seed;
    XwnMapRecord[3] = 10;
    return 0x4d504854;
}

VOID HalpXwnMapSnapshot(VOID)
{
    if (!XwnMapSeed || XwnMapSeed[3] != 30 || XwnMapSeed[24] != 80) for (;;) __halt();
    RtlCopyMemory((PVOID)XwnMapRecord, XwnMapSeed, 96*sizeof(ULONG));
    XwnMapRecord[0] = 0x564e5758;
    XwnMapSeed = NULL;
    XwnMapReady = TRUE;
}
#else
ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
    UNREFERENCED_PARAMETER(Seed); UNREFERENCED_PARAMETER(Signature); return 0;
}
#endif
