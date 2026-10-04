/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

#ifdef XBOX_NT5_MAP_PREFLIGHT
extern const UCHAR XwnMapFont[4096];
VOID HalpXwnMapEntry(VOID);
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
#define XWN_MAP_MAGIC 0x554e5758
#define XWN_MAP_SIGNATURE 0x50494e54
#define XWN_MAP_REPLY 0x50494854
#define XWN_MAP_TARGET 0x1590ab
#elif defined(XBOX_NT5_POOL_PREFLIGHT)
#define XWN_MAP_MAGIC 0x4f4e5758
#define XWN_MAP_SIGNATURE 0x504f4e54
#define XWN_MAP_REPLY 0x504f4854
#define XWN_MAP_TARGET 0x159067
#else
#define XWN_MAP_MAGIC 0x414e5758
#define XWN_MAP_SIGNATURE 0x50544e54
#define XWN_MAP_REPLY 0x50544854
#define XWN_MAP_TARGET 0x158518
#endif
static volatile ULONG XwnMapRecord[176] = {XWN_MAP_MAGIC,0x35544e50,1,0};
ULONG XwnPtBeforeTarget;
static UCHAR XwnPtBeforeOriginal[5];
static ULONG XwnPtDirectory[1024];
VOID HalpXwnPtBeforeEntry(VOID);
#elif defined(XBOX_NT5_SIZE_PREFLIGHT)
#define XWN_MAP_MAGIC 0x514e5758
#define XWN_MAP_SIGNATURE 0x535a4e54
#define XWN_MAP_REPLY 0x535a4854
#define XWN_MAP_TARGET 0x158439
static volatile ULONG XwnMapRecord[128] = {XWN_MAP_MAGIC,0x35544e50,1,0};
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
#define XWN_MAP_MAGIC 0x534e5758
#define XWN_MAP_SIGNATURE 0x53434e54
#define XWN_MAP_REPLY 0x53434854
#define XWN_MAP_TARGET 0x158025
static volatile ULONG XwnMapRecord[112] = {XWN_MAP_MAGIC,0x35544e50,1,0};
#else
#define XWN_MAP_MAGIC 0x564e5758
#define XWN_MAP_SIGNATURE 0x4d504e54
#define XWN_MAP_REPLY 0x4d504854
#define XWN_MAP_TARGET 0x157f3e
static volatile ULONG XwnMapRecord[96] = {XWN_MAP_MAGIC,0x35544e50,1,0};
#endif
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
#ifdef XBOX_NT5_PT_PREFLIGHT
    Valid = Valid && XwnMapRecord[128] && XwnMapRecord[135];
#ifdef XBOX_NT5_POOL_PREFLIGHT
    Valid = Valid && XwnMapRecord[147] && XwnMapRecord[149] == 504;
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
    Valid = Valid && XwnMapRecord[152] && XwnMapRecord[153];
    XwnMapRecord[24] = 150;
#else
    XwnMapRecord[24] = 140;
#endif
#else
    XwnMapRecord[24] = 130;
#endif
#elif defined(XBOX_NT5_SIZE_PREFLIGHT)
    Valid = Valid && XwnMapRecord[107] && XwnMapRecord[127];
    XwnMapRecord[24] = 120;
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
    Valid = Valid && XwnMapRecord[107];
    XwnMapRecord[24] = 110;
#else
    XwnMapRecord[24] = 100;
#endif
    XwnMapRecord[3] = Valid ? 90 : 40;
    if (XwnMapRecord[93])
    {
        volatile ULONG *Pixels = (volatile ULONG *)XwnMapRecord[92];
        for (I = 0; I < XwnMapRecord[21] / 4; ++I) Pixels[I] = 0xff000000;
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
        HalpXwnMapText(4, "XWN Windows 2000 nonpaged-pool initialization", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNU90: Pool initialized; PFN setup blocked."
                             : "XWNUFAIL: Pool-initialization guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Must-succeed pool pages: ", XwnMapRecord[154]);
        HalpXwnMapHex(12, "Free nonpaged-pool pages: ", XwnMapRecord[155]);
        HalpXwnMapHex(14, "Expansion PTEs initialized: ", XwnMapRecord[156]);
        HalpXwnMapHex(16, "Next candidate PFN: ", XwnMapRecord[140]);
        HalpXwnMapText(19, "Stopped BEFORE PFN backing allocation and storage.", 0xffffffff);
#elif defined(XBOX_NT5_POOL_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 initial nonpaged-pool mappings", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNO90: Pool backing mapped; initialization blocked."
                             : "XWNOFAIL: Pool-mapping guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Pool pages mapped: ", XwnMapRecord[149]);
        HalpXwnMapHex(12, "Pool virtual address: ", XwnMapRecord[150]);
        HalpXwnMapHex(14, "Next candidate PFN: ", XwnMapRecord[140]);
        HalpXwnMapHex(16, "Candidate pages remaining: ", XwnMapRecord[141]);
        HalpXwnMapText(19, "Stopped BEFORE pool initialization and PFN setup.", 0xffffffff);
#elif defined(XBOX_NT5_PT_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 first page-table allocation", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNA90: First page tables created; halted."
                             : "XWNAFAIL: Page-table guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Tables created and zeroed: ", XwnMapRecord[139]);
        HalpXwnMapHex(12, "First allocated PFN: ", XwnMapRecord[130]);
        HalpXwnMapHex(14, "Next candidate PFN: ", XwnMapRecord[140]);
        HalpXwnMapHex(16, "Candidate pages remaining: ", XwnMapRecord[141]);
        HalpXwnMapText(19, "Stopped BEFORE further MM allocation and PFN setup.", 0xffffffff);
#elif defined(XBOX_NT5_SIZE_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 memory sizing", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNQ90: Memory sizing complete; allocation blocked."
                             : "XWNQFAIL: Memory sizing validation failed.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Initial nonpaged pool bytes: ", XwnMapRecord[112]);
        HalpXwnMapHex(12, "PFN/color pages planned: ", XwnMapRecord[114]);
        HalpXwnMapHex(14, "Page-table pages planned: ", XwnMapRecord[126]);
        HalpXwnMapHex(16, "First candidate PFN: ", XwnMapRecord[120]);
        HalpXwnMapText(19, "Stopped BEFORE descriptor/page-table allocation.", 0xffffffff);
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 RAM descriptor scan", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNS90: RAM scan completed; allocation blocked."
                             : "XWNSFAIL: RAM scan validation failed.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Native RAM pages: ", XwnMapRecord[96]);
        HalpXwnMapHex(12, "Earlier limits pages: ", XwnMapRecord[110]);
        HalpXwnMapHex(14, "BIOS-reserved pages: ", XwnMapRecord[105]);
        HalpXwnMapText(17, "Candidate ranges checked; kernel bytes restored.", 0xffffffff);
        HalpXwnMapText(19, "Stopped BEFORE MM page allocation and PFN setup.", 0xffffffff);
#else
        HalpXwnMapText(4, "XWN Windows 2000 low-mapping transition", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNV90: Low mappings cleared; high HAL display active."
                             : "XWNVFAIL: Mapping checkpoint validation failed.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Absent low PDEs: ", Absent);
        HalpXwnMapHex(12, "CR3: ", XwnMapRecord[85]);
        HalpXwnMapHex(14, "Framebuffer VA: ", XwnMapRecord[92]);
        HalpXwnMapText(17, "TLB flushed; original kernel bytes restored.", 0xffffffff);
        HalpXwnMapText(19, "Stopped BEFORE RAM descriptor scan and storage.", 0xffffffff);
#endif
        HalpXwnMapText(22, "Photograph this screen, then reboot to dashboard.", 0xffffffff);
    }
    for (;;) __halt();
}

#ifdef XBOX_NT5_SCAN_PREFLIGHT
static VOID HalpXwnInspectScan(PULONG Frame, ULONG Largest)
{
    ULONG Count = 0, Total = 0, Limits = 0, Bios = 0, Low = MAXULONG, High = 0;
    ULONG Max = 0, LowMax = 0, MidMax = 0, MaxNode = 0, LowNode = 0;
    PLIST_ENTRY Head = &((PLOADER_PARAMETER_BLOCK)XwnMapRecord[4])->MemoryDescriptorListHead;
    PLIST_ENTRY Link;
    BOOLEAN Valid = XwnMapReady && (ULONG_PTR)Frame >= 0x80000000;
    if (!Valid) for (;;) __halt();
    for (Link = Head->Flink; Link != Head && Count < 128; Link = Link->Flink)
    {
        PMEMORY_ALLOCATION_DESCRIPTOR D = CONTAINING_RECORD(Link, MEMORY_ALLOCATION_DESCRIPTOR, ListEntry);
        ULONG Type = D->MemoryType, Base = D->BasePage, Pages = D->PageCount, Span;
        ++Count;
        if (!Pages || Base >= 0x4000 || Pages > 0x4000-Base) { Valid = FALSE; break; }
        if (Type == 26) Bios += Pages;
        if (Type == 6 || Type == 22 || Type == 23) continue;
        if (Type != 3) { Total += Pages; if (Type < 24) Limits += Pages; }
        if (Base < Low) Low = Base;
        if (Base+Pages-1 > High) High = Base+Pages-1;
        if (Type != 2 && Type != 4 && Type != 5 && Type != 8) continue;
        if (Pages > Max) { Max = Pages; MaxNode = (ULONG_PTR)D; }
        if (Base < 0x20000) { Span = min(Pages,0x20000-Base); if (Span > MidMax) MidMax = Span; }
        if (Base < 0x1000) { Span = min(Pages,0x1000-Base); if (Span > LowMax) { LowMax = Span; LowNode = (ULONG_PTR)D; } }
    }
    XwnMapRecord[96] = *(PULONG)(XwnMapRecord[6]+0x823d8);
    XwnMapRecord[97] = *(PULONG)(XwnMapRecord[6]+0x72734);
    XwnMapRecord[98] = *(PULONG)(XwnMapRecord[6]+0x81bb4);
    XwnMapRecord[99] = Largest;
    XwnMapRecord[100] = Frame[-13];
    XwnMapRecord[101] = Frame[-15];
    XwnMapRecord[102] = Frame[-16];
    XwnMapRecord[103] = Frame[-17];
    XwnMapRecord[104] = Total;
    XwnMapRecord[105] = Bios;
    XwnMapRecord[106] = Count;
#ifdef XBOX_NT5_SIZE_PREFLIGHT
    Valid = Valid && Link == Head && Count == 26 && Bios == 2 && Total-Limits == Bios &&
        XwnMapRecord[96] == Total && XwnMapRecord[97] == Low && XwnMapRecord[98] == High &&
        Largest == (MaxNode == LowNode ? 0 : MaxNode) && Frame[-13] == LowNode &&
        Frame[-16] == LowMax && Frame[-20] == (ULONG_PTR)Head;
#else
    Valid = Valid && Link == Head && Count == 26 && Bios == 2 && Total-Limits == Bios &&
        XwnMapRecord[96] == Total && XwnMapRecord[97] == Low && XwnMapRecord[98] == High &&
        Largest == MaxNode && Frame[-13] == LowNode && Frame[-15] == Max &&
        Frame[-16] == LowMax && Frame[-17] == MidMax && Frame[-20] == (ULONG_PTR)Head;
#endif
    XwnMapRecord[107] = Valid;
    XwnMapRecord[108] = MaxNode;
    XwnMapRecord[109] = LowNode;
    XwnMapRecord[110] = Limits;
    XwnMapRecord[111] = Frame[-20];
#ifdef XBOX_NT5_SIZE_PREFLIGHT
    {
        ULONG K = XwnMapRecord[6], Colors, PfnPages, Initial, Maximum, PoolStart, SystemStart;
        ULONG Groups = (Total - 0x400) >> 8, PfnBytes = ((High + 1) * 24) & ~4095;
        ULONG First, Last, I;
        PMEMORY_ALLOCATION_DESCRIPTOR D = (PMEMORY_ALLOCATION_DESCRIPTOR)LowNode;
        if (!Valid || !D) for (;;) __halt();
        XwnMapRecord[112] = *(PULONG)(K+0x82390);
        XwnMapRecord[113] = *(PULONG)(K+0x82320);
        XwnMapRecord[114] = Frame[-15];
        Colors = XwnMapRecord[115] = *(PULONG)(K+0x81b68);
        XwnMapRecord[116] = *(PULONG)(K+0x811c0);
        XwnMapRecord[117] = *(PULONG)(K+0x82330);
        First = XwnMapRecord[118] = Frame[-4];
        Last = XwnMapRecord[119] = Frame[-17];
        XwnMapRecord[120] = Frame[-2];
        XwnMapRecord[121] = Frame[-3];
        XwnMapRecord[122] = Frame[-21];
        XwnMapRecord[123] = Frame[-26];
        XwnMapRecord[124] = *(PULONG)(K+0x82498);
        XwnMapRecord[125] = Frame[-10];
        /* This pinned 64-MiB profile has no pool-size override or virtual bias. */
        Valid = Valid && Total == 0x3bff && High == 0x3bff && Colors >= 2 && Colors <= 0x400 &&
            !(Colors & (Colors-1)) && *(PULONG)(K+0x727e0) == 0x40000 &&
            *(PULONG)(K+0x727e4) == 0x8000 && *(PULONG)(K+0x727e8) == 0x100000 &&
            *(PULONG)(K+0x727ec) == 0x64000 && *(PULONG)(K+0x72ee0) == 0xffbe0000 &&
            !*(PULONG)(K+0x81bb0) && !*(PULONG)(K+0x823e0) && !*(PULONG)(K+0x73d30) &&
            !*(PULONG)(K+0x73d40) && !*(PULONG)(K+0x824a8) && !*(PULONG)(K+0x81178) &&
            *(PULONG)(K+0x81bfc) == 0x55f0;
        Initial = (0x40000 + Groups * 0x8000) & ~4095;
        PfnPages = (((High+1)*24 + Colors*16) >> 12) + 1;
        Maximum = min(0x8000000, max(PfnBytes + 0x100000 + Groups*0x64000, PfnBytes + Initial + 0x10000));
        Maximum += PfnPages << 12;
        PoolStart = (0xffbe0000 - Maximum) & ~4095;
        SystemStart = (PoolStart - ((0x55f0+1) << 12)) & 0xffc00000;
        Valid = Valid && XwnMapRecord[112] == Initial && XwnMapRecord[113] == Maximum &&
            Frame[-15] == PfnPages && XwnMapRecord[116] == PoolStart &&
            *(PULONG)(K+0x82278) == PoolStart && XwnMapRecord[117] == SystemStart &&
            First == 0xc0300000 + ((SystemStart >> 22)*4) && Last == 0xc0300ff8 &&
            SystemStart >= 0xeb000000 && Frame[-2] == D->BasePage && Frame[-3] == D->PageCount &&
            Frame[-21] == D->BasePage && Frame[-26] == D->PageCount &&
            XwnMapRecord[124] == High && !Frame[-10] && !Frame[-8] && !Frame[-11] &&
            !Frame[-12] && !Frame[-7] && First <= Last && First >= 0xc0300eb0;
        XwnMapRecord[126] = Valid ? ((Last-First)/4+1) : 0;
        if (Valid) for (I = First; I <= Last; I += 4)
            if (*(PULONG)I & 1) Valid = FALSE;
        Valid = Valid && XwnMapRecord[126] < D->PageCount &&
            XwnMapRecord[126] <= LowMax && D->BasePage > 2;
        XwnMapRecord[127] = Valid;
    }
#endif
}
DECLSPEC_NORETURN VOID NTAPI HalpXwnScanCheckpoint(PULONG Frame, ULONG Largest)
{
    HalpXwnInspectScan(Frame, Largest);
    HalpXwnMapCheckpoint(Frame);
}
#endif

#ifdef XBOX_NT5_PT_PREFLIGHT
static ULONG HalpXwnDescriptorHash(VOID)
{
    PLIST_ENTRY Head = &((PLOADER_PARAMETER_BLOCK)XwnMapRecord[4])->MemoryDescriptorListHead, Link;
    ULONG Hash = 2166136261UL, Count = 0, I;
    for (Link = Head->Flink; Link != Head && Count < 128; Link = Link->Flink)
    {
        PULONG D = (PULONG)Link;
        for (I = 0; I < 5; ++I) Hash = (Hash ^ D[I]) * 16777619UL;
        ++Count;
    }
    return Link == Head && Count == 26 ? Hash : 0;
}
VOID NTAPI HalpXwnPtBefore(PULONG Frame, ULONG Largest)
{
    ULONG Base, Count, I, J, Cr0, Cr3 = __readcr3(), Pde, Pfn;
    BOOLEAN Valid;
    HalpXwnInspectScan(Frame, Largest);
    Base = XwnMapRecord[120]; Count = XwnMapRecord[126];
    Valid = XwnMapRecord[107] && XwnMapRecord[127] && !Largest && Count == 28 &&
        Base == 0x160 && XwnMapRecord[121] == 0x2000 && (Frame[-6]&0xfff) == 0x163;
    XwnMapRecord[129] = Count; XwnMapRecord[130] = Base; XwnMapRecord[131] = Frame[-3];
    XwnMapRecord[132] = Cr3; XwnMapRecord[136] = (ULONG_PTR)Frame;
    XwnMapRecord[137] = XwnPtBeforeTarget; XwnMapRecord[138] = (ULONG_PTR)HalpXwnPtBeforeEntry;
    XwnMapRecord[143] = Frame[-6] & 0xfff;
#ifdef XBOX_NT5_POOL_PREFLIGHT
    /* Admit only the audited low-memory path: no extra PDE/direct-map branch. */
    {
        ULONG K = XwnMapRecord[6];
        Valid = Valid && !Frame[-14] && !Frame[-19] &&
            !*(PULONG)(K+0x8232c) && !*(PULONG)(K+0x812b8) &&
            !*(PUCHAR)(K+0x82384) && *(PULONG)(K+0x822a0) == 0xa0000000 &&
            *(PULONG)(K+0x81bac) == 0x7f00 && !*(PULONG)(K+0x811a0) &&
            XwnMapRecord[112] == 0x1f8000 && XwnMapRecord[116] == 0xfe4af000;
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
        Valid = Valid && *(PULONG)(K+0x727f4) == 0x4000 && !*(PULONG)(K+0x73dec) &&
            XwnMapRecord[113] == 0x1731000;
        XwnMapRecord[152] = Valid;
#endif
        Count += 504;
        XwnMapRecord[147] = Valid; XwnMapRecord[148] = Count;
    }
#endif
    /* Reject reuse of any actively mapped frame, directory or page table. */
    if ((Cr3>>12) >= Base && (Cr3>>12) < Base+Count) Valid = FALSE;
    for (I = 0; Valid && I < 1024; ++I)
    {
        Pde = ((volatile ULONG *)0xc0300000)[I];
        if (!(Pde&1)) continue;
        if (Pde&0x80) { Valid = FALSE; break; }
        Pfn = Pde>>12;
        if (Pfn >= Base && Pfn < Base+Count) { Valid = FALSE; break; }
        for (J = 0; J < 1024; ++J)
        {
            ULONG Pte = ((volatile ULONG *)(0xc0000000 + I*4096))[J];
            Pfn = Pte>>12;
            if ((Pte&1) && Pfn >= Base && Pfn < Base+Count) { Valid = FALSE; break; }
        }
    }
    XwnMapRecord[134] = Valid;
    XwnMapRecord[144] = HalpXwnDescriptorHash();
    Valid = Valid && XwnMapRecord[144] && *(PUCHAR)XwnPtBeforeTarget == 0xe9 &&
        XwnPtBeforeTarget+5+*(PULONG)(XwnPtBeforeTarget+1) == (ULONG_PTR)HalpXwnPtBeforeEntry;
    XwnMapRecord[128] = Valid;
    if (!Valid) HalpXwnMapCheckpoint(Frame);
    for (I = 0; I < 1024; ++I) XwnPtDirectory[I] = ((volatile ULONG *)0xc0300000)[I];
    Cr0 = __readcr0(); _disable(); __writecr0(Cr0 & ~0x10000);
    RtlCopyMemory((PVOID)XwnPtBeforeTarget, XwnPtBeforeOriginal, 5);
    __writecr0(Cr0);
    XwnMapRecord[133] = memcmp((PVOID)XwnPtBeforeTarget, XwnPtBeforeOriginal, 5) == 0;
    if (!XwnMapRecord[133]) HalpXwnMapCheckpoint(Frame);
}
DECLSPEC_NORETURN VOID NTAPI HalpXwnPtAfter(PULONG Frame, ULONG Largest)
{
    ULONG I, J, Base = XwnMapRecord[130], Count = XwnMapRecord[129];
    ULONG First = (XwnMapRecord[118]-0xc0300000)/4, Last = (XwnMapRecord[119]-0xc0300000)/4;
    BOOLEAN Valid = XwnMapRecord[128] && XwnMapRecord[133] && (ULONG_PTR)Frame == XwnMapRecord[136] &&
        __readcr3() == XwnMapRecord[132] && !Largest && Count == 28 && Last-First+1 == Count;
    XwnMapRecord[140] = Frame[-2]; XwnMapRecord[141] = Frame[-3]; XwnMapRecord[142] = Frame[-4];
    XwnMapRecord[145] = HalpXwnDescriptorHash();
#ifdef XBOX_NT5_POOL_PREFLIGHT
    XwnMapRecord[150] = *(PULONG)(XwnMapRecord[6]+0x811c0);
    Valid = Valid && XwnMapRecord[147] && XwnMapRecord[148] == 532 &&
        XwnMapRecord[145] == XwnMapRecord[144] &&
        Frame[-2] == Base+Count+504 && Frame[-3] == XwnMapRecord[131]-Count-504 &&
        Frame[-4] == XwnMapRecord[119]+4 && !Frame[-8] && !Frame[-10] && !Frame[-11] && !Frame[-12] &&
        !Frame[-7] && !Frame[-19] && Frame[-6] == 0xfe4af000 && Frame[-17] == 0x1f8000 &&
        XwnMapRecord[150] == 0xfe4af000 && *(PULONG)(XwnMapRecord[6]+0x82390) == 0x1f8000;
#else
    Valid = Valid && XwnMapRecord[145] == XwnMapRecord[144] &&
        Frame[-2] == Base+Count && Frame[-3] == XwnMapRecord[131]-Count &&
        Frame[-4] == XwnMapRecord[119]+4 && !Frame[-8] && !Frame[-10] && !Frame[-11] && !Frame[-12];
#endif
    for (I = 0; Valid && I < 1024; ++I)
    {
        ULONG Pde = ((volatile ULONG *)0xc0300000)[I];
        if (I >= First && I <= Last)
        {
            if (Pde != ((Base+I-First)<<12 | XwnMapRecord[143])) { Valid = FALSE; break; }
            for (J = 0; J < 1024; ++J)
            {
                ULONG Expected = 0;
#ifdef XBOX_NT5_POOL_PREFLIGHT
                ULONG Va = (I << 22) | (J << 12);
                if (Va >= 0xfe4af000 && Va < 0xfe6a7000)
                {
                    Expected = ((Base+Count+((Va-0xfe4af000)>>12))<<12) | 0x163;
                    ++XwnMapRecord[149];
                }
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
                else if (Va == 0xfe6a8000) Expected = 0xfffff000;
                else if (Va == 0xfe6a9000) Expected = 0x01538000;
#endif
#endif
                if (((volatile ULONG *)(0xc0000000+I*4096))[J] != Expected) { Valid = FALSE; break; }
            }
            if (Valid) ++XwnMapRecord[139];
        }
        else if ((Pde & ~0x60) != (XwnPtDirectory[I] & ~0x60)) Valid = FALSE;
    }
    XwnMapRecord[146] = Valid;
    XwnMapRecord[135] = Valid && XwnMapRecord[139] == Count;
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
    if (XwnMapRecord[135])
    {
        ULONG K = XwnMapRecord[6], Pool = 0xfe4af000, Free = Pool+0x4000, Head = K+0x81338;
        XwnMapRecord[154] = *(PULONG)(K+0x82268);
        XwnMapRecord[155] = *(PULONG)(K+0x81b80);
        XwnMapRecord[156] = *(PULONG)(K+0x8121c);
        XwnMapRecord[157] = *(PULONG)(K+0x81384);
        XwnMapRecord[158] = *(PULONG)(K+0x8125c);
        XwnMapRecord[159] = *(PULONG)(K+0x81264);
        XwnMapRecord[160] = Head; XwnMapRecord[161] = Free;
        XwnMapRecord[165] = *(PULONG)(K+0x81388);
        XwnMapRecord[166] = *(PULONG)(K+0x81378);
        Valid = XwnMapRecord[152] && XwnMapRecord[154] == 4 && XwnMapRecord[155] == 500 &&
            XwnMapRecord[156] == 5432 && XwnMapRecord[157] == 0xfe6a7000 &&
            XwnMapRecord[158] == 0xc03f9aa0 && XwnMapRecord[159] == 0xc03fef7c &&
            XwnMapRecord[165] == 0x373 && XwnMapRecord[166] == 0x9ff &&
            *(PULONG)(K+0x824a4) == Pool && *(PULONG)(K+0x81ac0) == 504 &&
            *(PULONG)(K+0x82334) == 0xc0200000 && *(PULONG)(K+0x8239c) == 0x7e6a8000 &&
            *(PULONG)Head == Free && *(PULONG)(Head+4) == Free &&
            *(PULONG)Free == Head && *(PULONG)(Free+4) == Head && *(PULONG)(Free+8) == 500;
        for (I = 0; Valid && I < 3; ++I)
            if (*(PULONG)(K+0x81320+I*8) != K+0x81320+I*8 ||
                *(PULONG)(K+0x81324+I*8) != K+0x81320+I*8) Valid = FALSE;
        for (I = 0; Valid && I < 4; ++I)
        {
            if (*(PULONG)(Pool+I*4096) != (I == 3 ? 0 : Pool+(I+1)*4096)) Valid = FALSE;
            else ++XwnMapRecord[163];
        }
        for (I = 0; Valid && I < 500; ++I)
        {
            if (*(PULONG)(Free+I*4096+16) != Free) Valid = FALSE;
            else ++XwnMapRecord[162];
        }
        XwnMapRecord[164] = XwnMapRecord[135];
        XwnMapRecord[153] = Valid;
    }
#endif
    HalpXwnMapCheckpoint(Frame);
}
#endif

ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
    UCHAR Expected[8] = {0xa1,0,0,0,0,0x33,0xff,0x48};
#elif defined(XBOX_NT5_POOL_PREFLIGHT)
    static const UCHAR Expected[8] = {0x8b,0x45,0xe8,0x89,0x4d,0xbc,0x03,0xc1};
#else
    UCHAR Expected[8] = {0x33,0xc0,0x39,0x05,0,0,0,0};
#endif
    static const UCHAR BeforeExpected[8] = {0x8b,0x72,0x10,0x03,0x72,0x0c,0x39,0x75};
#elif defined(XBOX_NT5_SIZE_PREFLIGHT)
    static const UCHAR Expected[8] = {0x8b,0x72,0x10,0x03,0x72,0x0c,0x39,0x75};
#elif defined(XBOX_NT5_SCAN_PREFLIGHT)
    static const UCHAR Expected[8] = {0x8b,0x4d,0xcc,0x3b,0xcb,0x75,0x02,0x33};
#else
    static const UCHAR Expected[8] = {0x8b,0x45,0x08,0x33,0xdb,0x8d,0x48,0x08};
#endif
    PIMAGE_NT_HEADERS Nt;
    ULONG Cr0;
    if (!Seed || Signature != XWN_MAP_SIGNATURE || XwnMapSeed || Seed[6] < 0x80000000 ||
        Seed[7] != 1691648 || Seed[11] != __readcr3() || Seed[20] < 0x03c00000 ||
        !((Seed[17]==640 && Seed[18]==480 && Seed[19]==2560) ||
          (Seed[17]==1024 && Seed[18]==576 && Seed[19]==4096)) ||
        Seed[21] != Seed[18]*Seed[19] || Seed[20] > 0x04000000-Seed[21]) return 0;
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_POOLINIT_PREFLIGHT
    *(PULONG)(Expected+1) = Seed[6]+0x81b68;
#elif !defined(XBOX_NT5_POOL_PREFLIGHT)
    *(PULONG)(Expected+4) = Seed[6]+0x823e0;
#endif
    if (memcmp((PVOID)(Seed[6]+0x158439), BeforeExpected, sizeof(BeforeExpected))) return 0;
#endif
    Nt = (PIMAGE_NT_HEADERS)(Seed[6] + ((PIMAGE_DOS_HEADER)Seed[6])->e_lfanew);
    if (Nt->Signature != IMAGE_NT_SIGNATURE || Nt->FileHeader.TimeDateStamp != 1266293717 ||
        Nt->OptionalHeader.CheckSum != 1747402 || Nt->OptionalHeader.AddressOfEntryPoint != 44560 ||
        memcmp((PVOID)(Seed[6]+XWN_MAP_TARGET), Expected, sizeof(Expected))) return 0;
    RtlCopyMemory((PVOID)XwnMapRecord, Seed, 96*sizeof(ULONG));
    XwnMapRecord[0] = XWN_MAP_MAGIC;
    if (!HalpXwnDisplayMapped()) { XwnMapRecord[3] = 0; return 0; }
    XwnMapTarget = (PUCHAR)(Seed[6]+XWN_MAP_TARGET);
    RtlCopyMemory(XwnMapOriginal, XwnMapTarget, 5);
    Cr0 = __readcr0(); _disable(); __writecr0(Cr0 & ~0x10000);
#ifdef XBOX_NT5_PT_PREFLIGHT
    XwnPtBeforeTarget = Seed[6]+0x158439;
    RtlCopyMemory(XwnPtBeforeOriginal, (PVOID)XwnPtBeforeTarget, 5);
    *(PUCHAR)XwnPtBeforeTarget = 0xe9;
    *(PULONG)(XwnPtBeforeTarget+1) = (ULONG_PTR)HalpXwnPtBeforeEntry-(XwnPtBeforeTarget+5);
#endif
    XwnMapTarget[0] = 0xe9;
    *(PULONG)(XwnMapTarget+1) = (ULONG_PTR)HalpXwnMapEntry-(ULONG_PTR)(XwnMapTarget+5);
    __writecr0(Cr0);
    Seed[80] = (ULONG_PTR)XwnMapTarget;
    Seed[88] = (ULONG_PTR)HalpXwnMapEntry;
    XwnMapSeed = Seed;
    XwnMapRecord[3] = 10;
    return XWN_MAP_REPLY;
}

VOID HalpXwnMapSnapshot(VOID)
{
    if (!XwnMapSeed || XwnMapSeed[3] != 30 || XwnMapSeed[24] != 80) for (;;) __halt();
    RtlCopyMemory((PVOID)XwnMapRecord, XwnMapSeed, 96*sizeof(ULONG));
    XwnMapRecord[0] = XWN_MAP_MAGIC;
    XwnMapSeed = NULL;
    XwnMapReady = TRUE;
}
#else
ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
    UNREFERENCED_PARAMETER(Seed); UNREFERENCED_PARAMETER(Signature); return 0;
}
#endif
