/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

#ifdef XBOX_NT5_MAP_PREFLIGHT
extern const UCHAR XwnMapFont[4096];
VOID HalpXwnMapEntry(VOID);
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
#define XWN_MAP_MAGIC 0x474e5758
#define XWN_MAP_SIGNATURE 0x464c4e54
#define XWN_MAP_REPLY 0x464c4854
#define XWN_MAP_TARGET 0x159898
#define XWN_EXPANSION_FREE 5340
ULONG XwnCommitTarget;
static UCHAR XwnCommitOriginal[5];
VOID HalpXwnCommitEntry(VOID);
#elif defined(XBOX_NT5_PFNCOMMIT_PREFLIGHT)
#define XWN_MAP_MAGIC 0x4a4e5758
#define XWN_MAP_SIGNATURE 0x50434e54
#define XWN_MAP_REPLY 0x50434854
#define XWN_MAP_TARGET 0x1596f3
#define XWN_EXPANSION_FREE 5340
#elif defined(XBOX_NT5_PFNMAP_PREFLIGHT)
#define XWN_MAP_MAGIC 0x4c4e5758
#define XWN_MAP_SIGNATURE 0x50444e54
#define XWN_MAP_REPLY 0x50444854
#define XWN_MAP_TARGET 0x159684
#define XWN_EXPANSION_FREE 5340
#elif defined(XBOX_NT5_PFN_PREFLIGHT)
#define XWN_MAP_MAGIC 0x454e5758
#define XWN_MAP_SIGNATURE 0x50464e54
#define XWN_MAP_REPLY 0x50464854
#define XWN_MAP_TARGET 0x159416
#define XWN_EXPANSION_FREE 5340
#elif defined(XBOX_NT5_POOLINIT_PREFLIGHT)
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
#ifndef XWN_EXPANSION_FREE
#define XWN_EXPANSION_FREE 5432
#endif
static volatile ULONG XwnMapRecord[256] = {XWN_MAP_MAGIC,0x35544e50,1,0};
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
            (ULONG_PTR)Frame >= 0x80000000 &&
#ifndef XBOX_NT5_FREELIST_PREFLIGHT
            Frame[2] == XwnMapRecord[4] &&
#endif
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    RtlCopyMemory((PVOID)XwnCommitTarget,XwnCommitOriginal,5);
    XwnMapRecord[197]=memcmp((PVOID)XwnCommitTarget,XwnCommitOriginal,5)==0;
#endif
    __writecr0(Cr0);
    XwnMapRecord[87] = memcmp(XwnMapTarget, XwnMapOriginal, 5) == 0;
    XwnMapRecord[81] = 0;
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    XwnMapRecord[82] = XwnMapRecord[4];
#else
    XwnMapRecord[82] = Frame[2];
#endif
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
#ifdef XBOX_NT5_PFN_PREFLIGHT
    Valid = Valid && XwnMapRecord[167] && XwnMapRecord[168] && XwnMapRecord[175];
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
    Valid = Valid && XwnMapRecord[178] && XwnMapRecord[187];
#ifdef XBOX_NT5_PFNCOMMIT_PREFLIGHT
    Valid = Valid && XwnMapRecord[195];
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    Valid=Valid && XwnMapRecord[198] && XwnMapRecord[214] && XwnMapRecord[197];
    XwnMapRecord[24] = 190;
#else
    XwnMapRecord[24] = 180;
#endif
#else
    XwnMapRecord[24] = 170;
#endif
#else
    XwnMapRecord[24] = 160;
#endif
#else
    XwnMapRecord[24] = 150;
#endif
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
        HalpXwnMapText(4, "XWN Windows 2000 free-page lists", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNG90: Free-page lists built; reserved pages protected."
                             : "XWNGFAIL: Free-list guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Free pages verified: ", XwnMapRecord[211]);
        HalpXwnMapHex(12, "New in-use PFNs: ", XwnMapRecord[212]);
        HalpXwnMapHex(14, "Protected loaded images: ", XwnMapRecord[215]);
        HalpXwnMapHex(16, "PFN records checked: ", XwnMapRecord[222]);
        HalpXwnMapText(19, "Stopped BEFORE further MM initialization and storage.", 0xffffffff);
#elif defined(XBOX_NT5_PFNCOMMIT_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 descriptor accounting", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNJ90: Descriptor accounting reconciled; lists blocked."
                             : "XWNJFAIL: Descriptor accounting guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Candidate first PFN: ", XwnMapRecord[188]);
        HalpXwnMapHex(12, "Native remaining pages: ", XwnMapRecord[189]);
        HalpXwnMapHex(14, "Reconciled remaining pages: ", XwnMapRecord[194]);
        HalpXwnMapHex(16, "Double-counted pages restored: ", XwnMapRecord[192]);
        HalpXwnMapText(19, "Stopped BEFORE free-page lists and storage.", 0xffffffff);
#elif defined(XBOX_NT5_PFNMAP_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 mapped PFN initialization", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNL90: Mapped PFNs initialized; TLB flushed."
                             : "XWNLFAIL: Mapped-PFN guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "Page directories processed: ", XwnMapRecord[179]);
        HalpXwnMapHex(12, "Present PTEs processed: ", XwnMapRecord[180]);
        HalpXwnMapHex(14, "Populated PFN records: ", XwnMapRecord[182]);
        HalpXwnMapHex(16, "Color-list heads: ", XwnMapRecord[183]);
        HalpXwnMapText(19, "Stopped BEFORE free-page lists and storage.", 0xffffffff);
#elif defined(XBOX_NT5_PFN_PREFLIGHT)
        HalpXwnMapText(4, "XWN Windows 2000 PFN backing allocation", 0xffffffff);
        HalpXwnMapText(7, Valid ? "XWNE90: PFN backing mapped and cleared."
                             : "XWNEFAIL: PFN-backing guard stopped execution.", Valid ? 0xff00ff00 : 0xffff0000);
        HalpXwnMapHex(10, "PFN database VA: ", XwnMapRecord[169]);
        HalpXwnMapHex(12, "PFN backing pages: ", XwnMapRecord[170]);
        HalpXwnMapHex(14, "Color backing pages: ", XwnMapRecord[171]);
        HalpXwnMapHex(16, "Next candidate PFN: ", XwnMapRecord[140]);
        HalpXwnMapText(19, "Stopped BEFORE PFN/color population and storage.", 0xffffffff);
#elif defined(XBOX_NT5_POOLINIT_PREFLIGHT)
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
        for (I = 0; I < 5; ++I)
        {
            ULONG Value = D[I];
#ifdef XBOX_NT5_PFN_PREFLIGHT
            /* Compare every original descriptor field; separately validate
             * the one native base/count commit at the final boundary. */
            if ((ULONG_PTR)D == XwnMapRecord[100] && I == 3) Value = XwnMapRecord[120];
            if ((ULONG_PTR)D == XwnMapRecord[100] && I == 4) Value = XwnMapRecord[121];
#endif
            Hash = (Hash ^ Value) * 16777619UL;
        }
        ++Count;
    }
    return Link == Head && Count == 26 ? Hash : 0;
}
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
static ULONG XwnPfnExpected[0x3c00][6];
static ULONG HalpXwnPfnMask(ULONG Pte)
{
    if (Pte <= XwnMapRecord[185]) return 5;
    if (Pte >= 0xc0300000 && Pte < 0xc0303000)
        return Pte <= XwnMapRecord[186] ? 5 : 1;
    return XwnMapRecord[184] | 1;
}
/* Hash every original table except the recursive directory. Its exact
 * expected allocation/permission changes are checked separately below. */
static ULONG HalpXwnExistingPtes(BOOLEAN Project)
{
    ULONG I, J, Hash = 2166136261UL;
    for (I = 512; I < 1024; ++I)
    {
        if (I == 768 || !(XwnPtDirectory[I]&1)) continue;
        for (J = 0; J < 1024; ++J)
        {
            ULONG Address = 0xc0000000+I*4096+J*4;
            ULONG Value = *(PULONG)Address;
            if (Project && (Value&1)) Value |= HalpXwnPfnMask(Address);
            Hash = (Hash ^ (Value & ~0x60)) * 16777619UL;
        }
    }
    return Hash;
}
static VOID HalpXwnExpectedPfn(ULONG Pfn, ULONG Pte, ULONG Parent)
{
    PULONG Row = XwnPfnExpected[Pfn];
    Row[1] = Pte; ++Row[2];
    Row[3] = ((Row[3] | 0x10000) & 0xfffffe8f) | 0x600;
    Row[5] = Parent;
}
static BOOLEAN HalpXwnMappedPfns(VOID)
{
    ULONG K = XwnMapRecord[6], I, J, Pfn, Parent, Va, Pte, Value;
    PULONG Directory = (PULONG)0xc0300000;
    PULONG Actual = (PULONG)0xffb85000;
    BOOLEAN Valid = XwnMapRecord[184] == *(PULONG)(K+0x73df0) &&
        XwnMapRecord[185] == *(PULONG)(K+0x82270) &&
        XwnMapRecord[186] == *(PULONG)(K+0x823a4) &&
        !*(PULONG)(K+0x823e0) && !*(PUCHAR)(K+0x82384);
    XwnMapRecord[177] = HalpXwnExistingPtes(FALSE);
    XwnMapRecord[187] = XwnMapRecord[176] == XwnMapRecord[177];
    Valid = Valid && XwnMapRecord[187];
    RtlZeroMemory(XwnPfnExpected, sizeof(XwnPfnExpected));
    Parent = Directory[768] >> 12;
    for (I = 512; Valid && I < 1024; ++I)
    {
        if (!(Directory[I]&1)) continue;
        Pfn = Directory[I] >> 12;
        if ((Directory[I]&0x80) || Pfn >= 0x3c00) { Valid = FALSE; break; }
        HalpXwnExpectedPfn(Pfn, 0xc0300000+I*4, Parent);
        ++XwnMapRecord[179];
        for (J = 0; J < 1024; ++J)
        {
            Pte = 0xc0000000+I*4096+J*4; Value = *(PULONG)Pte;
            if (!(Value&1)) continue;
            ++XwnPfnExpected[Pfn][2]; ++XwnMapRecord[180];
            Va = (I<<22) | (J<<12);
            if (Va >= 0xa0000000 && (Value>>12) < 0x3c00)
            {
                HalpXwnExpectedPfn(Value>>12, Pte, Pfn);
                ++XwnMapRecord[181];
            }
        }
    }
    for (I = 0; Valid && I < 0x3c00; ++I)
    {
        for (J = 0; J < 6; ++J)
            if (Actual[I*6+J] != XwnPfnExpected[I][J]) { Valid = FALSE; break; }
        if (XwnPfnExpected[I][3] >> 16) ++XwnMapRecord[182];
    }
    Actual = (PULONG)0xffbdf000;
    for (I = 0; Valid && I < 1024; ++I)
    {
        ULONG Expected = (I < 128 && !(I&1)) ? MAXULONG : 0;
        if (Actual[I] != Expected) { Valid = FALSE; break; }
        if (Expected) ++XwnMapRecord[183];
    }
    XwnMapRecord[178] = Valid && XwnMapRecord[183] == 64;
    return XwnMapRecord[178];
}
#endif
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
static ULONG XwnFreeColors[1024], XwnFreeHead[4], XwnCommitFrame[32];
static ULONG HalpXwnAllMappings(VOID)
{
    ULONG I,J,Value,Hash=2166136261UL;
    PULONG Directory=(PULONG)0xc0300000,Table;
    for (I=0;I<1024;++I)
    {
        Value=Directory[I];Hash=(Hash^(Value&~0x60UL))*16777619UL;
        if (!(Value&1)) continue;
        if ((Value&0x80) || (Value>>12)>=0x3c00) return 0;
        Table=(PULONG)(0xc0000000+I*4096);
        for (J=0;J<1024;++J) Hash=(Hash^(Table[J]&~0x60UL))*16777619UL;
    }
    return Hash;
}
static BOOLEAN HalpXwnEvents(BOOLEAN After)
{
    ULONG K = XwnMapRecord[6], I;
    static const ULONG Offsets[3] = {0x81dc0,0x812a0,0x81c20};
    for (I=0; I<3; ++I)
    {
        PULONG E=(PULONG)(K+Offsets[I]);
        if (E[0] != (I==2 ? 0x40001 : 0x40000) || E[1] != (I==2 && !After ? 0 : 1) ||
            E[2] != (ULONG_PTR)(E+2) || E[3] != (ULONG_PTR)(E+2)) return FALSE;
    }
    return *(PUCHAR)(K+0x81b48) == (After ? 1 : 0);
}
static BOOLEAN HalpXwnProtectedRange(ULONG Va, ULONG Size)
{
    ULONG End, Pfn, Pte;
    if (!Size || Va < 0x80000000 || Va+Size < Va) return FALSE;
    End=Va+Size; Va &= ~0xfffUL;
    while (Va < End)
    {
        if (!(((PULONG)0xc0300000)[Va>>22]&1)) return FALSE;
        Pte=*(PULONG)(0xc0000000+(Va>>12)*4); Pfn=Pte>>12;
        if (!(Pte&1) || Pfn>=0x3c00 || !(XwnPfnExpected[Pfn][3]>>16) ||
            ((XwnPfnExpected[Pfn][3]>>8)&7)!=6) return FALSE;
        Va+=4096;
    }
    return TRUE;
}
static BOOLEAN HalpXwnPrepareFree(PULONG Frame)
{
    ULONG K=XwnMapRecord[6], I,J,Count=0,Type,Base,Pages,Pfn,Va,Previous,Color;
    PLIST_ENTRY Head=(PLIST_ENTRY)(XwnMapRecord[4]+8),Link;
    PULONG Row,D,Free=(PULONG)(K+0x72768);
    if (*(PULONG)(K+0x727bc)!=(ULONG_PTR)Free || Free[0] || Free[1]!=1 ||
        Free[2]!=MAXULONG || Free[3]!=MAXULONG || *(PULONG)(K+0x81bf8) ||
        *(PULONG)(K+0x8119c)!=31 || *(PULONG)(K+0x727d8)!=8 ||
        !HalpXwnEvents(FALSE)) return FALSE;
    XwnMapRecord[209]=(ULONG_PTR)Free;
    RtlCopyMemory(XwnFreeHead,Free,sizeof(XwnFreeHead));
    RtlZeroMemory(XwnFreeColors,sizeof(XwnFreeColors));
    for (I=0;I<64;++I) XwnFreeColors[I*2]=MAXULONG;
    for (Link=Head->Blink;Link!=Head && Count<26;Link=Link->Blink,++Count)
    {
        D=(PULONG)Link; Type=D[2];Base=D[3];Pages=D[4];
        if (Base>=0x4000 || Pages>0x4000-Base || Type==3) return FALSE;
        if (Type==6 || Type==22 || Type==23) Pages=Base>=0x3c00 ? 0 : min(Pages,0x3c00-Base);
        for (Pfn=Base;Pfn<Base+Pages;++Pfn)
        {
            if (Pfn>=0x3c00) return FALSE;
            Row=XwnPfnExpected[Pfn];
            if (Type==2 || Type==4 || Type==5 || Type==8)
            {
                if (Row[3]>>16) { ++XwnMapRecord[213];continue; }
                if (Row[3]&0x2000) return FALSE;
                Row[1]=Pfn<<2; Previous=XwnFreeHead[3];
                if (Previous==MAXULONG) XwnFreeHead[2]=Pfn;
                else XwnPfnExpected[Previous][0]=Pfn;
                XwnFreeHead[3]=Pfn; ++XwnFreeHead[0];
                Row[0]=MAXULONG;Row[2]=Previous;Row[3]=(Row[3]&~0x700UL)|0x100;
                Color=64+(Pfn&31)*2;
                if (XwnFreeColors[Color]==MAXULONG) XwnFreeColors[Color]=Pfn;
                else
                {
                    Previous=(XwnFreeColors[Color+1]-0xffb85000)/24;
                    if (Previous>=0x3c00) return FALSE;
                    XwnPfnExpected[Previous][4]=Pfn;
                }
                XwnFreeColors[Color+1]=0xffb85000+Pfn*24;Row[4]=MAXULONG;
            }
            else if (!(Row[3]>>16))
            {
                Va=0x80000000+(Pfn<<12);
                Row[1]=0xc0000000+(Va>>12)*4;++Row[2];
                Row[3]=(((Row[3]&0xffff)|0x10000)&0xfffffe8f)|0x600;
                Row[5]=((PULONG)0xc0300000)[Va>>22]>>12;
                ++XwnMapRecord[212];
            }
            else ++XwnMapRecord[213];
        }
    }
    if (Link!=Head || Count!=26) return FALSE;
    XwnMapRecord[210]=XwnFreeHead[0];
    /* Every loaded image page, hive, live frame and firmware page must
     * retain a nonzero reference and active state in the predicted walk. */
    Head=(PLIST_ENTRY)XwnMapRecord[4];Count=0;
    for (Link=Head->Flink;Link!=Head && Count<20;Link=Link->Flink,++Count)
    {
        D=(PULONG)Link;
        if (!HalpXwnProtectedRange(D[6],D[8])) return FALSE;
    }
    if (Link!=Head || Count!=20 || !HalpXwnProtectedRange(XwnMapRecord[4],92) ||
        !HalpXwnProtectedRange((ULONG_PTR)Frame,12) ||
        *(PULONG)(XwnMapRecord[4]+40)!=1810432 ||
        !HalpXwnProtectedRange(*(PULONG)(XwnMapRecord[4]+44),1810432)) return FALSE;
    XwnMapRecord[215]=Count;
    for (I=0;I<1024;++I)
    {
        J=((PULONG)0xc0300000)[I];
        if ((J&1) && ((J&0x80) || (J>>12)>=0x3c00 || !(XwnPfnExpected[J>>12][3]>>16))) return FALSE;
    }
    for (I=0;I<3;++I) if (!(XwnPfnExpected[I][3]>>16)) return FALSE;
    XwnMapRecord[216]=1;
    RtlCopyMemory(XwnCommitFrame,Frame-26,29*sizeof(ULONG));
    XwnMapRecord[208]=(ULONG_PTR)(XwnCommitFrame+26);
    XwnMapRecord[236]=HalpXwnAllMappings();
    if (!XwnMapRecord[236]) return FALSE;
    XwnMapRecord[217]=1;
    return TRUE;
}
DECLSPEC_NORETURN VOID NTAPI HalpXwnFreeAfter(PULONG Frame, ULONG Largest)
{
    ULONG K=XwnMapRecord[6],I,J,Hash;
    PULONG Pfn=(PULONG)0xffb85000,Colors=(PULONG)0xffbdf000;
    BOOLEAN Valid=XwnMapRecord[198] && XwnMapRecord[197] && XwnMapRecord[217] &&
        !Largest && (ULONG_PTR)Frame==XwnMapRecord[136] && __readcr3()==XwnMapRecord[132];
    XwnMapRecord[227]=Frame[2];XwnMapRecord[228]=Frame[-18];XwnMapRecord[229]=Frame[-12];
    Valid=Valid && Frame[-19]==XwnMapRecord[4]+8 && Frame[-20]==XwnMapRecord[4]+8;
    Hash=HalpXwnDescriptorHash();XwnMapRecord[221]=Hash;
    Valid=Valid && Hash==XwnMapRecord[196] && *(PULONG)(XwnMapRecord[100]+12)==0x3cf &&
        *(PULONG)(XwnMapRecord[100]+16)==0x1d91;
    for (I=0;Valid && I<0x3c00;++I)
    {
        for (J=0;J<6;++J) if (Pfn[I*6+J]!=XwnPfnExpected[I][J]) { Valid=FALSE;break; }
        if (Valid) ++XwnMapRecord[222];
    }
    for (I=0;Valid && I<1024;++I)
    {
        if (Colors[I]!=XwnFreeColors[I]) {Valid=FALSE;break;}
        ++XwnMapRecord[223];
    }
    XwnMapRecord[219]=XwnMapRecord[223]==1024;
    for (I=0;Valid && I<4;++I) if (((PULONG)XwnMapRecord[209])[I]!=XwnFreeHead[I]) Valid=FALSE;
    XwnMapRecord[211]=*(PULONG)XwnMapRecord[209];
    XwnMapRecord[218]=*(PULONG)(K+0x81bf8);
    XwnMapRecord[230]=((PULONG)XwnMapRecord[209])[2];XwnMapRecord[231]=((PULONG)XwnMapRecord[209])[3];
    XwnMapRecord[220]=HalpXwnEvents(TRUE);
    XwnMapRecord[232]=KeGetPcr()->Irql;XwnMapRecord[233]=KeGetPcr()->IRR;
    XwnMapRecord[234]=__inbyte(0x21)|(__inbyte(0xa1)<<8);
    XwnMapRecord[235]=*(PULONG)(K+0x727bc)==XwnMapRecord[209] &&
        *(PULONG)(K+0x811b8)==0xffbdf000 && *(PULONG)(K+0x811bc)==0xffbdf100 &&
        *(PULONG)(K+0x8119c)==31 && *(PULONG)(K+0x727d8)==8;
    XwnMapRecord[237]=HalpXwnAllMappings();
    XwnMapRecord[214]=Valid && XwnMapRecord[211]==XwnMapRecord[210] &&
        XwnMapRecord[218]==XwnMapRecord[210] && XwnMapRecord[220] && XwnMapRecord[235] &&
        XwnMapRecord[232]==APC_LEVEL && !XwnMapRecord[233] && XwnMapRecord[234]==0xffff &&
        KeGetPcr()->IDR==0xfffffffb && (__readeflags()&0x200) &&
        XwnMapRecord[237]==XwnMapRecord[236] && HalpXwnExistingPtes(FALSE)==XwnMapRecord[177];
    HalpXwnMapCheckpoint(Frame);
}
#endif

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
#ifdef XBOX_NT5_PFN_PREFLIGHT
        Valid = Valid && XwnMapRecord[114] == 91 && XwnMapRecord[115] == 32 &&
            KeGetPcr()->Irql == APC_LEVEL && !KeGetPcr()->IRR &&
            KeGetPcr()->IDR == 0xfffffffb &&
            __inbyte(0x21) == 0xff && __inbyte(0xa1) == 0xff;
        XwnMapRecord[167] = Valid;
        Count += 91;
#endif
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
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
    XwnMapRecord[184] = *(PULONG)(XwnMapRecord[6]+0x73df0);
    XwnMapRecord[185] = *(PULONG)(XwnMapRecord[6]+0x82270);
    XwnMapRecord[186] = *(PULONG)(XwnMapRecord[6]+0x823a4);
    XwnMapRecord[176] = HalpXwnExistingPtes(TRUE);
#endif
    Cr0 = __readcr0(); _disable(); __writecr0(Cr0 & ~0x10000);
    RtlCopyMemory((PVOID)XwnPtBeforeTarget, XwnPtBeforeOriginal, 5);
    __writecr0(Cr0);
    XwnMapRecord[133] = memcmp((PVOID)XwnPtBeforeTarget, XwnPtBeforeOriginal, 5) == 0;
    if (!XwnMapRecord[133]) HalpXwnMapCheckpoint(Frame);
}
#ifndef XBOX_NT5_FREELIST_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID NTAPI HalpXwnPtAfter(PULONG Frame, ULONG Largest)
{
    ULONG I, J, Base = XwnMapRecord[130], Count = XwnMapRecord[129];
    ULONG First = (XwnMapRecord[118]-0xc0300000)/4, Last = (XwnMapRecord[119]-0xc0300000)/4;
    BOOLEAN Valid = XwnMapRecord[128] && XwnMapRecord[133] && (ULONG_PTR)Frame == XwnMapRecord[136] &&
        __readcr3() == XwnMapRecord[132] && !Largest && Count == 28 && Last-First+1 == Count;
    XwnMapRecord[140] = Frame[-2]; XwnMapRecord[141] = Frame[-3]; XwnMapRecord[142] = Frame[-4];
    XwnMapRecord[145] = HalpXwnDescriptorHash();
#ifdef XBOX_NT5_POOL_PREFLIGHT
    XwnMapRecord[150] = *(PULONG)(XwnMapRecord[6]+0x811c0);
#ifdef XBOX_NT5_PFN_PREFLIGHT
    {
        PULONG D = (PULONG)XwnMapRecord[100];
#ifdef XBOX_NT5_PFNCOMMIT_PREFLIGHT
        /* This pinned single-candidate path commits the PFN allocation
         * twice using the original base. Record the native undercount;
         * require the full model before reconciling its remaining extent. */
        XwnMapRecord[188] = D[3]; XwnMapRecord[189] = D[4];
        XwnMapRecord[190] = XwnMapRecord[120]+XwnMapRecord[121];
        XwnMapRecord[191] = Frame[-21];
        XwnMapRecord[175] = D[2] == 5 && D[3] == 0x3cf && D[4] == 0x1b23 &&
            Frame[-21] == XwnMapRecord[120] && XwnMapRecord[190] == 0x2160 &&
#else
        XwnMapRecord[175] = D[3] == 0x3ce && D[4] == 0x1d92 &&
#endif
            XwnMapRecord[145] == XwnMapRecord[144];
        Valid = Valid && XwnMapRecord[147] && XwnMapRecord[148] == 623 &&
            XwnMapRecord[175] && Frame[-2] == 0x3cf && Frame[-3] == 0x1d91 &&
            Frame[-4] == 0xc03fef7c &&
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
            !Frame[-8] && Frame[-14] == 0xc0300c00 && Frame[-12] == 0xc0301000 &&
            !Frame[-10] && !Frame[-11] && !Frame[-7] &&
#else
            Frame[-8] == 0x3ce && Frame[-14] == 0x1d92 &&
            !Frame[-10] && !Frame[-11] && !Frame[-12] && !Frame[-7] && !Frame[-19] &&
#endif
            Frame[-6] == 0xfe4af000 && Frame[-17] == 0x1f8000 &&
            XwnMapRecord[150] == 0xfe4af000 && *(PULONG)(XwnMapRecord[6]+0x82390) == 0x1f8000;
    }
#else
    Valid = Valid && XwnMapRecord[147] && XwnMapRecord[148] == 532 &&
        XwnMapRecord[145] == XwnMapRecord[144] &&
        Frame[-2] == Base+Count+504 && Frame[-3] == XwnMapRecord[131]-Count-504 &&
        Frame[-4] == XwnMapRecord[119]+4 && !Frame[-8] && !Frame[-10] && !Frame[-11] && !Frame[-12] &&
        !Frame[-7] && !Frame[-19] && Frame[-6] == 0xfe4af000 && Frame[-17] == 0x1f8000 &&
        XwnMapRecord[150] == 0xfe4af000 && *(PULONG)(XwnMapRecord[6]+0x82390) == 0x1f8000;
#endif
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
            ULONG ExpectedPde = ((Base+I-First)<<12) | XwnMapRecord[143];
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
            ExpectedPde |= HalpXwnPfnMask(0xc0000000+I*4096) | HalpXwnPfnMask(0xc0300000+I*4);
#endif
            if (Pde != ExpectedPde) { Valid = FALSE; break; }
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
                else if (Va == 0xfe6a9000) Expected = XWN_EXPANSION_FREE << 12;
#ifdef XBOX_NT5_PFN_PREFLIGHT
                else if (Va >= 0xffb85000 && Va < 0xffbe0000)
                    Expected = ((0x374+((Va-0xffb85000)>>12))<<12) | 0x163;
#endif
#endif
#endif
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
                if (Expected&1) Expected |= HalpXwnPfnMask(0xc0000000+I*4096+J*4);
#endif
                if (((volatile ULONG *)(0xc0000000+I*4096))[J] != Expected) { Valid = FALSE; break; }
            }
            if (Valid) ++XwnMapRecord[139];
        }
        else
        {
            ULONG Expected = XwnPtDirectory[I];
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
            if (Expected&1) Expected |= HalpXwnPfnMask(0xc0000000+I*4096) | HalpXwnPfnMask(0xc0300000+I*4);
#endif
            if ((Pde & ~0x60) != (Expected & ~0x60)) Valid = FALSE;
        }
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
            XwnMapRecord[156] == XWN_EXPANSION_FREE && XwnMapRecord[157] == 0xfe6a7000 &&
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
#ifdef XBOX_NT5_PFN_PREFLIGHT
        XwnMapRecord[169] = *(PULONG)(K+0x81ab0);
        XwnMapRecord[172] = __inbyte(0x21) | (__inbyte(0xa1)<<8);
        XwnMapRecord[173] = KeGetPcr()->Irql; XwnMapRecord[174] = KeGetPcr()->IRR;
        Valid = Valid && XwnMapRecord[167] && XwnMapRecord[169] == 0xffb85000 &&
            *(PULONG)(K+0x72ee0) == 0xffb85000 && *(PULONG)(K+0x8130c) == 91 &&
            *(PULONG)(K+0x811b8) == 0xffbdf000 && *(PULONG)(K+0x811bc) == 0xffbdf100 &&
            XwnMapRecord[172] == 0xffff && XwnMapRecord[173] == APC_LEVEL &&
            !XwnMapRecord[174] && KeGetPcr()->IDR == 0xfffffffb;
#ifdef XBOX_NT5_PFNMAP_PREFLIGHT
        if (Valid) Valid = HalpXwnMappedPfns();
        if (Valid) { XwnMapRecord[170] = 90; XwnMapRecord[171] = 1; }
#else
        for (I = 0; Valid && I < 91; ++I)
        {
            PULONG Page = (PULONG)(0xffb85000+(I<<12));
            for (J = 0; J < 1024; ++J) if (Page[J]) { Valid = FALSE; break; }
            if (Valid) ++XwnMapRecord[I == 90 ? 171 : 170];
        }
#endif
        XwnMapRecord[168] = Valid && XwnMapRecord[170] == 90 && XwnMapRecord[171] == 1;
#endif
    }
#endif
#ifdef XBOX_NT5_PFNCOMMIT_PREFLIGHT
    /* Only a validated snapshot may restore the 622 pages omitted by the
     * repeated subtraction. Consumed PFNs 160..3ce remain excluded. The
     * console still halts here; this never creates or allocates a free list. */
    if (XwnMapRecord[135] && XwnMapRecord[153] && XwnMapRecord[168] &&
        XwnMapRecord[175] && XwnMapRecord[178] && XwnMapRecord[187] &&
        Frame[-2] == XwnMapRecord[188] && Frame[-3] == XwnMapRecord[190]-Frame[-2] &&
        Frame[-3] == XwnMapRecord[189]+622)
    {
        PULONG D = (PULONG)XwnMapRecord[100];
        XwnMapRecord[192] = Frame[-3]-D[4];
        D[4] = Frame[-3];
        XwnMapRecord[193] = D[3]; XwnMapRecord[194] = D[4];
        XwnMapRecord[196] = HalpXwnDescriptorHash();
        XwnMapRecord[195] = D[3] == 0x3cf && D[4] == 0x1d91 &&
            D[3]+D[4] == XwnMapRecord[190] && XwnMapRecord[196] == XwnMapRecord[144];
    }
#endif
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    if (XwnMapRecord[195] && HalpXwnPrepareFree(Frame))
    {
        ULONG Cr0=__readcr0();
        _disable();__writecr0(Cr0&~0x10000UL);
        RtlCopyMemory((PVOID)XwnCommitTarget,XwnCommitOriginal,5);
        __writecr0(Cr0);
        XwnMapRecord[197]=memcmp((PVOID)XwnCommitTarget,XwnCommitOriginal,5)==0;
        XwnMapRecord[198]=XwnMapRecord[197];
        if (XwnMapRecord[198]) return; /* Assembly restores registers/flags. */
    }
#endif
    HalpXwnMapCheckpoint(Frame);
}
#endif

ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    UCHAR Expected[8] = {0x80,0x7d,0xfe,0x00,0x8b,0x15,0,0};
    static const UCHAR CommitExpected[8]={0x8b,0x45,0x08,0x8b,0x40,0x0c,0xe9,0x8e};
#elif defined(XBOX_NT5_PFNCOMMIT_PREFLIGHT)
    UCHAR Expected[8] = {0x8b,0x45,0x08,0x8b,0x40,0x0c,0xe9,0x8e};
#elif defined(XBOX_NT5_PFNMAP_PREFLIGHT)
    UCHAR Expected[8] = {0xa1,0,0,0,0,0x8b,0x15,0xb0};
#elif defined(XBOX_NT5_PFN_PREFLIGHT)
    UCHAR Expected[8] = {0x33,0xc9,0x39,0x0d,0,0,0,0};
#elif defined(XBOX_NT5_POOLINIT_PREFLIGHT)
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    *(PUSHORT)(Expected+6)=(USHORT)(Seed[6]+0x81ab0);
    if (memcmp((PVOID)(Seed[6]+0x1596f3),CommitExpected,8)) return 0;
#elif defined(XBOX_NT5_PFNCOMMIT_PREFLIGHT)
    /* All eight pinned bytes are position independent. */
#elif defined(XBOX_NT5_PFNMAP_PREFLIGHT)
    *(PULONG)(Expected+1) = Seed[6]+0x72734;
#elif defined(XBOX_NT5_PFN_PREFLIGHT)
    *(PULONG)(Expected+4) = Seed[6]+0x81b68;
#elif defined(XBOX_NT5_POOLINIT_PREFLIGHT)
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    XwnCommitTarget=Seed[6]+0x1596f3;
    RtlCopyMemory(XwnCommitOriginal,(PVOID)XwnCommitTarget,5);
    *(PUCHAR)XwnCommitTarget=0xe9;
    *(PULONG)(XwnCommitTarget+1)=(ULONG_PTR)HalpXwnCommitEntry-(XwnCommitTarget+5);
    XwnMapRecord[224]=XwnCommitTarget;XwnMapRecord[225]=(ULONG_PTR)HalpXwnCommitEntry;
    Seed[94]=XwnCommitTarget;Seed[95]=(ULONG_PTR)HalpXwnCommitEntry;
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
#ifdef XBOX_NT5_FREELIST_PREFLIGHT
    XwnMapRecord[224]=XwnMapRecord[94];XwnMapRecord[225]=XwnMapRecord[95];
#endif
    XwnMapReady = TRUE;
}
#else
ULONG NTAPI XwnConfigureMapProbe(PULONG Seed, ULONG Signature)
{
    UNREFERENCED_PARAMETER(Seed); UNREFERENCED_PARAMETER(Signature); return 0;
}
#endif
