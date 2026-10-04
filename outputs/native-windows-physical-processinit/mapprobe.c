/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

#ifdef XBOX_NT5_MAP_PREFLIGHT
extern const UCHAR XwnMapFont[4096];
VOID HalpXwnMapEntry(VOID);
#ifdef XBOX_NT5_PT_PREFLIGHT
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
#define XWN_MAP_MAGIC 0x574e5758
#define XWN_MAP_SIGNATURE 0x57494e54
#define XWN_MAP_REPLY 0x57494854
#define XWN_MAP_TARGET 0x159cdc
#define XWN_EXPANSION_FREE 5340
ULONG XwnCommitTarget,XwnFreeTarget,XwnSysTarget,XwnProcessTarget;
static UCHAR XwnCommitOriginal[5],XwnFreeOriginal[5],XwnSysOriginal[5],XwnProcessOriginal[5];
VOID HalpXwnCommitEntry(VOID);
VOID HalpXwnFreeEntry(VOID);
VOID HalpXwnSysEntry(VOID);
VOID HalpXwnProcessEntry(VOID);
#elif defined(XBOX_NT5_PROCESSPAGES_PREFLIGHT)
#define XWN_MAP_MAGIC 0x5a4e5758
#define XWN_MAP_SIGNATURE 0x50524e54
#define XWN_MAP_REPLY 0x50524854
#define XWN_MAP_TARGET 0x159ca0
#define XWN_EXPANSION_FREE 5340
ULONG XwnCommitTarget,XwnFreeTarget,XwnSysTarget;
static UCHAR XwnCommitOriginal[5],XwnFreeOriginal[5],XwnSysOriginal[5];
VOID HalpXwnCommitEntry(VOID);
VOID HalpXwnFreeEntry(VOID);
VOID HalpXwnSysEntry(VOID);
#elif defined(XBOX_NT5_SYSPTES_PREFLIGHT)
#define XWN_MAP_MAGIC 0x594e5758
#define XWN_MAP_SIGNATURE 0x53594e54
#define XWN_MAP_REPLY 0x53594854
#define XWN_MAP_TARGET 0x159bd7
#define XWN_EXPANSION_FREE 5340
ULONG XwnCommitTarget,XwnFreeTarget;
static UCHAR XwnCommitOriginal[5],XwnFreeOriginal[5];
VOID HalpXwnCommitEntry(VOID);
VOID HalpXwnFreeEntry(VOID);
#elif defined(XBOX_NT5_FREELIST_PREFLIGHT)
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
static volatile ULONG XwnMapRecord[320] = {XWN_MAP_MAGIC,0x35544e50,1,0};
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
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    RtlCopyMemory((PVOID)XwnProcessTarget,XwnProcessOriginal,5);
    XwnMapRecord[290]=memcmp((PVOID)XwnProcessTarget,XwnProcessOriginal,5)==0;
#endif
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
    RtlCopyMemory((PVOID)XwnSysTarget,XwnSysOriginal,5);
    XwnMapRecord[258]=memcmp((PVOID)XwnSysTarget,XwnSysOriginal,5)==0;
#endif
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
    RtlCopyMemory((PVOID)XwnFreeTarget,XwnFreeOriginal,5);
    XwnMapRecord[254]=memcmp((PVOID)XwnFreeTarget,XwnFreeOriginal,5)==0;
#endif
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
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
    Valid=Valid && XwnMapRecord[240] && XwnMapRecord[241] && XwnMapRecord[254];
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
    Valid=Valid && XwnMapRecord[259] && XwnMapRecord[261] && XwnMapRecord[258];
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    Valid=Valid && XwnMapRecord[290] && XwnMapRecord[291] && XwnMapRecord[293];
    XwnMapRecord[24]=220;
#else
    XwnMapRecord[24]=210;
#endif
#else
    XwnMapRecord[24]=200;
#endif
#else
    XwnMapRecord[24] = 190;
#endif
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
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
        HalpXwnMapText(4,"XWN Windows 2000 process address space",0xffffffff);
        HalpXwnMapText(7,Valid?"XWNW90: Process address space initialized.":"XWNWFAIL: Process initialization guard stopped.",Valid?0xff00ff00:0xffff0000);
        HalpXwnMapHex(10,"Native return status: ",XwnMapRecord[304]);
        HalpXwnMapHex(12,"Working-set entries: ",4);
        HalpXwnMapHex(14,"Hash-table PFN: ",XwnMapRecord[294]);
        HalpXwnMapHex(16,"Free pages remaining: ",XwnMapRecord[295]);
        HalpXwnMapText(19,"Stopped BEFORE further MM initialization and storage.",0xffffffff);
#elif defined(XBOX_NT5_PROCESSPAGES_PREFLIGHT)
        HalpXwnMapText(4,"XWN Windows 2000 first process pages",0xffffffff);
        HalpXwnMapText(7,Valid?"XWNZ90: First process pages allocated and zeroed.":"XWNZFAIL: Process-page guard stopped execution.",Valid?0xff00ff00:0xffff0000);
        HalpXwnMapHex(10,"Page-table PFN: ",XwnMapRecord[262]);
        HalpXwnMapHex(12,"Working-set PFN: ",XwnMapRecord[263]);
        HalpXwnMapHex(14,"Free pages remaining: ",XwnMapRecord[264]);
        HalpXwnMapHex(16,"Executive pool list heads: ",XwnMapRecord[269]);
        HalpXwnMapText(19,"Stopped BEFORE working-set publication and process init.",0xffffffff);
#elif defined(XBOX_NT5_SYSPTES_PREFLIGHT)
        HalpXwnMapText(4,"XWN Windows 2000 system PTE initialization",0xffffffff);
        HalpXwnMapText(7,Valid ? "XWNY90: System PTEs initialized; page allocation blocked." : "XWNYFAIL: System-PTE guard stopped execution.",Valid?0xff00ff00:0xffff0000);
        HalpXwnMapHex(10,"System PTEs initialized: ",XwnMapRecord[243]);
        HalpXwnMapHex(12,"Cached PTEs / blocks: ",XwnMapRecord[244]);
        HalpXwnMapHex(14,"Cache blocks verified: ",XwnMapRecord[245]);
        HalpXwnMapHex(16,"Remaining system PTEs: ",XwnMapRecord[246]);
        HalpXwnMapText(19,"Stopped BEFORE executive pool and process-page allocation.",0xffffffff);
#elif defined(XBOX_NT5_FREELIST_PREFLIGHT)
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
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
static ULONG XwnTailFrame[32];
static const ULONG XwnCacheSizes[5]={1,2,4,8,16},XwnCacheCounts[5]={400,100,60,50,40};
static ULONG HalpXwnTailMappings(VOID)
{
    ULONG I,J,V,H=2166136261UL,A;PULONG D=(PULONG)0xc0300000,T;
    for(I=0;I<1024;++I){V=D[I];H=(H^(V&~0x60UL))*16777619UL;if(!(V&1))continue;
        if((V&0x80)||(V>>12)>=0x3c00)return 0;T=(PULONG)(0xc0000000+I*4096);
        for(J=0;J<1024;++J){A=(ULONG_PTR)&T[J];V=(A>=0xc03e3000 && A<0xc03f92b8)?0:T[J];H=(H^(V&~0x60UL))*16777619UL;}}
    return H;
}
static BOOLEAN HalpXwnPrepareTail(PULONG F)
{
    ULONG I,K=XwnMapRecord[6];
    if(F[-7] || (F[-1]&0xff0000) || F[-16] || F[-17]!=0x1f8000 || F[-6]!=0xfe4af000 ||
       F[-21]!=0x160 || F[-26]!=0x2000 || F[-13]!=XwnMapRecord[100] ||
       *(PULONG)(K+0x72734)!=1 || *(PULONG)(K+0x82498)!=0x3bff ||
       *(PULONG)(K+0x824a4)!=0xfe4af000 || *(PULONG)(K+0x727f4)!=0x4000 ||
       *(PULONG)(K+0x82330)!=0xf8c00000 || *(PULONG)(K+0x82390)!=0x1f8000 ||
       *(PULONG)(K+0x81bfc)!=22000 || *(PULONG)(K+0x81178) || *(PULONG)(K+0x73dec))return FALSE;
    for(I=0xc03e3000;I<0xc03f92b8;I+=4)if(*(PULONG)I)return FALSE;
    for(I=0;I<5;++I){
        if(*(PULONG)(K+0x72e50+I*4)!=XwnCacheSizes[I] || *(PULONG)(K+0x81220+I*4) ||
           *(PULONG)(K+0x81240+I*4) || *(PULONG)(K+0x81280+I*4))return FALSE;}
    if(*(PULONG)(K+0x81218)||*(PULONG)(K+0x81258)||*(PULONG)(K+0x81260)||
       *(PULONG)(K+0x82398)||*(PULONG)(K+0x81268)||*(PULONG)(K+0x81254))return FALSE;
    if((*(PULONG)0xc03fee14>>12)!=0x374 || (*(PULONG)0xc03fef78>>12)!=0x3cd)return FALSE;
    XwnPfnExpected[0x374][3]|=2;XwnPfnExpected[0x3cd][3]|=4;
    for(I=0;I<4;++I){if((*(PULONG)(0xc03f92bc+4*I)>>12)!=0x17c+I)return FALSE;XwnPfnExpected[0x17c+I][3]|=6;}
    RtlCopyMemory(XwnTailFrame,F-26,29*sizeof(ULONG));XwnMapRecord[250]=(ULONG_PTR)(XwnTailFrame+26);
    XwnMapRecord[247]=HalpXwnTailMappings();return XwnMapRecord[247]!=0;
}
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
static ULONG XwnProcessBytes[192],XwnProcessFrame[32];
static ULONG HalpXwnProcessMappings(VOID)
{
    ULONG I,J,V,A,H=2166136261UL;PULONG D=(PULONG)0xc0300000,T;
    for(I=0;I<1024;++I){V=I==769?0:D[I];H=(H^(V&~0x60UL))*16777619UL;if(!(V&1))continue;
        if((V&0x80)||(V>>12)>=0x3c00)return 0;T=(PULONG)(0xc0000000+I*4096);
        for(J=0;J<1024;++J){A=(ULONG_PTR)&T[J];V=A==0xc0300c04?0:T[J];H=(H^(V&~0x60UL))*16777619UL;}}
    return H;
}
static BOOLEAN HalpXwnRemoveModel(ULONG Slot)
{
    ULONG P=XwnFreeColors[64],Next,Prev,I;PULONG Row;
    if(P>=0x3c00 || XwnFreeHead[0]<=28)return FALSE;
    Row=XwnPfnExpected[P];if((Row[3]>>16) || ((Row[3]>>8)&7)!=1 || (P&31))return FALSE;
    Next=Row[0];Prev=Row[2];
    if(Next!=0xffffffff && Next>=0x3c00)return FALSE;
    if(Prev!=0xffffffff && Prev>=0x3c00)return FALSE;
    if(Next==0xffffffff)XwnFreeHead[3]=Prev;else XwnPfnExpected[Next][2]=Prev;
    if(Prev==0xffffffff)XwnFreeHead[2]=Next;else XwnPfnExpected[Prev][0]=Next;
    --XwnFreeHead[0];XwnFreeColors[64]=Row[4];
    I=(Row[3]>>4)&7;Row[0]=Row[2]=0;Row[3]=(Row[3]&0xffff0000)|(I<<4);
    XwnMapRecord[Slot]=P;return TRUE;
}
static BOOLEAN HalpXwnPrepareProcess(PULONG F)
{
    ULONG I,J,K=XwnMapRecord[6],Process,Old=F[-24];PULONG P;
    if(*(PULONG)0xc0300c04 || Old!=(__readcr3()>>12) || Old>=0x3c00 ||
       (*(PULONG)(K+0x76068)&0x400) || *(PULONG)(K+0x72ec8)!=0x63 || *(PULONG)(K+0x72eb4)!=0x63 ||
       *(PULONG)(K+0x72810)!=26 || *(PULONG)(K+0x81bf8)!=XwnMapRecord[210])return FALSE;
    for(I=0;I<2;++I){P=(PULONG)(K+(I?0x75600:0x74ca0));for(J=0;J<0x108;++J)if(P[J])return FALSE;}
    if(*(PULONG)(K+0x755f0)||*(PULONG)(K+0x755f8)||*(PULONG)(K+0x7534c)||*(PULONG)(K+0x6ca9c))return FALSE;
    if(*(PULONG)(K+0x81ab8)||*(PULONG)(K+0x81b90)||*(PULONG)(K+0x82374)||*(PULONG)(K+0x81aa8))return FALSE;
    Process=*(PULONG)(*(PULONG)0xffdff124+0x44);
    if(Process<K || Process+sizeof(XwnProcessBytes)>K+XwnMapRecord[7])return FALSE;
    RtlCopyMemory(XwnProcessBytes,(PVOID)Process,sizeof(XwnProcessBytes));
    XwnMapRecord[265]=Process;XwnMapRecord[266]=Old;
    RtlCopyMemory(XwnProcessFrame,F-26,29*sizeof(ULONG));XwnMapRecord[284]=(ULONG_PTR)(XwnProcessFrame+26);
    XwnMapRecord[277]=HalpXwnProcessMappings();if(!XwnMapRecord[277])return FALSE;
    if(!HalpXwnRemoveModel(262) || !HalpXwnRemoveModel(263))return FALSE;
    if(Old==XwnMapRecord[262] || Old==XwnMapRecord[263] || !(XwnPfnExpected[Old][3]>>16))return FALSE;
    XwnPfnExpected[Old][2]=0;XwnPfnExpected[Old][3]&=0xffff;
    XwnMapRecord[260]=1;return TRUE;
}
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
static ULONG XwnInitThread[112];
static BOOLEAN HalpXwnPrepareInit(ULONG Process)
{
    ULONG K=XwnMapRecord[6],I,P,Old=XwnMapRecord[266],Table=XwnMapRecord[262],Ws=XwnMapRecord[263];PULONG R;
    if(*(PULONG)(K+0x81b60)||*(PULONG)(K+0x823e0)||*(PULONG)(K+0x81e08)||*(PULONG)(K+0x82340)||
       *(PULONG)(K+0x72830)!=50||*(PULONG)(K+0x72834)!=450||*(PULONG)(K+0x72ee8)!=0x7c000||*(PULONG)(K+0x72920)!=2||
       *(PULONG)(K+0x73de8)||*(PULONG)0xffdf0014||*(PULONG)0xffdf0018||*(PULONG)0xffdf001c)return FALSE;
    if(XwnProcessBytes[0xdc/4]||XwnProcessBytes[0x114/4])return FALSE;
    XwnMapRecord[306]=*(PULONG)0xffdff124;RtlCopyMemory(XwnInitThread,(PVOID)XwnMapRecord[306],sizeof(XwnInitThread));
    if(!HalpXwnRemoveModel(294))return FALSE;P=XwnMapRecord[294];
    if(P==Old||P==Table||P==Ws)return FALSE;
    R=XwnPfnExpected[Old];R[0]=Process;R[1]=0xc0300c00;R[2]=3;R[3]=0x10601;R[4]=0x80;R[5]=Old;
    R=XwnPfnExpected[Table];R[0]=1;R[1]=0xc0300c04;R[2]=3;R[3]=0x10601;R[4]=0x80;R[5]=Old;
    R=XwnPfnExpected[Ws];R[0]=2;R[1]=0xc0301404;R[2]=1;R[3]=0x10601;R[4]=0x80;R[5]=Table;
    R=XwnPfnExpected[P];R[0]=3;R[1]=0xc0301bc8;R[2]=1;R[3]=0x10601;R[4]=0x80;R[5]=Table;
    XwnProcessBytes[0xd0/4]=XwnProcessBytes[0xd4/4]=0;
    XwnProcessBytes[0xdc/4]=1;XwnProcessBytes[0xe0/4]=XwnProcessBytes[0xe4/4]=4;
    XwnProcessBytes[0xe8/4]=50;XwnProcessBytes[0xec/4]=450;XwnProcessBytes[0xf0/4]=0xc0501000;
    XwnProcessBytes[0x114/4]=1;XwnProcessBytes[0x130/4]=1;XwnProcessBytes[0x138/4]=0;
    ((PUCHAR)XwnProcessBytes)[0x13c]=1;((PUCHAR)XwnProcessBytes)[0x13e]=4;XwnProcessBytes[0x140/4]=0;
    XwnProcessBytes[0x144/4]=XwnProcessBytes[0x148/4]=Process+0x144;XwnProcessBytes[0x150/4]=Ws;
    ((PUCHAR)XwnProcessBytes)[0x156]=2;XwnProcessBytes[0x158/4]=1;XwnProcessBytes[0x160/4]=0;
    ((PUCHAR)XwnProcessBytes)[0x164]=1;((PUCHAR)XwnProcessBytes)[0x166]=4;XwnProcessBytes[0x168/4]=0;
    XwnProcessBytes[0x16c/4]=XwnProcessBytes[0x170/4]=Process+0x16c;
    XwnProcessBytes[0x1e8/4]=XwnProcessBytes[0x1ec/4]=Process+0x1e8;XwnProcessBytes[0x280/4]=0;
    XwnMapRecord[292]=1;return TRUE;
}
DECLSPEC_NORETURN VOID NTAPI HalpXwnInitAfter(PULONG F,ULONG Process,ULONG Status)
{
    ULONG I,J,K=XwnMapRecord[6],Value,Third=XwnMapRecord[294];BOOLEAN Valid;
    XwnMapRecord[304]=Status;
    Valid=XwnMapRecord[291] && XwnMapRecord[292] && !Status && Process==XwnMapRecord[265] &&
        (ULONG_PTR)F==XwnMapRecord[136] && F[1]==K+0x155b55 && __readcr3()==XwnMapRecord[132];
    for(I=0;Valid && I<0x3c00;++I)for(J=0;J<6;++J)if(((PULONG)0xffb85000)[I*6+J]!=XwnPfnExpected[I][J]){Valid=FALSE;break;}
    for(I=0;Valid && I<1024;++I)if(((PULONG)0xffbdf000)[I]!=XwnFreeColors[I])Valid=FALSE;
    for(I=0;I<4;++I)if(((PULONG)XwnMapRecord[209])[I]!=XwnFreeHead[I])Valid=FALSE;
    XwnMapRecord[297]=Valid;XwnMapRecord[295]=*(PULONG)(K+0x81bf8);
    XwnMapRecord[296]=memcmp((PVOID)Process,XwnProcessBytes,sizeof(XwnProcessBytes))==0;
    XwnMapRecord[305]=*(PULONG)0xffdff124==XwnMapRecord[306] && memcmp((PVOID)XwnMapRecord[306],XwnInitThread,sizeof(XwnInitThread))==0;
    XwnMapRecord[299]=(*(PULONG)0xc0300c04&~0x60UL)==((XwnMapRecord[262]<<12)|3);
    for(I=0;XwnMapRecord[299] && I<1024;++I){Value=I==257?((XwnMapRecord[263]<<12)|3):(I==0||I==754)?((Third<<12)|3):0;
        if((((PULONG)0xc0301000)[I]&(Value?~0x60UL:~0UL))!=Value)XwnMapRecord[299]=0;}
    XwnMapRecord[298]=XwnMapRecord[300]=0;
    if(XwnMapRecord[299]){
        XwnMapRecord[298]=XwnMapRecord[300]=1;
        for(I=0;I<1024;++I){Value=0;
            if(I==0||I==3)Value=50;else if(I==1||I==2)Value=4;else if(I==4)Value=3;
            else if(I==5)Value=0xc0501694;else if(I==7)Value=0x25a;else if(I==9||I==11)Value=0xc06f2000;
            else if(I==10)Value=0x200;else if(I==12)Value=0xc0800000;
            else if(I==421)Value=0xc0300203;else if(I==422)Value=0xc0301203;else if(I==423)Value=0xc0501203;else if(I==424)Value=0xc06f2203;
            else if(I>=425 && I<1023)Value=(I-420)<<4;else if(I==1023)Value=0xfffffff0;
            if(((PULONG)0xc0501000)[I]!=Value)XwnMapRecord[298]=0;
            if(((PULONG)0xc06f2000)[I])XwnMapRecord[300]=0;}
    }
    XwnMapRecord[301]=HalpXwnProcessMappings();XwnMapRecord[302]=XwnMapRecord[277];XwnMapRecord[303]=KeGetPcr()->Irql;
    XwnMapRecord[293]=Valid && XwnMapRecord[296] && XwnMapRecord[298] && XwnMapRecord[299] && XwnMapRecord[300] &&
        XwnMapRecord[305] && XwnMapRecord[295]+3==XwnMapRecord[210] && XwnMapRecord[301]==XwnMapRecord[302] &&
        XwnMapRecord[303]==APC_LEVEL && !KeGetPcr()->IRR && KeGetPcr()->IDR==0xfffffffb &&
        (__readeflags()&0x200) && __inbyte(0x21)==0xff && __inbyte(0xa1)==0xff &&
        *(PULONG)(K+0x81e08)==1 && *(PULONG)(K+0x82340)==1 && HalpXwnDescriptorHash()==XwnMapRecord[144];
    HalpXwnMapCheckpoint(F);
}
#endif

#ifndef XBOX_NT5_PROCESSINIT_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID NTAPI HalpXwnProcessAfter(PULONG F,ULONG Process)
{
    ULONG I,J,K=XwnMapRecord[6],V,A;PULONG P,C=(PULONG)0xffbdf000;BOOLEAN Valid;
    Valid=XwnMapRecord[259] && XwnMapRecord[260] && Process==XwnMapRecord[265] &&
        (ULONG_PTR)F==XwnMapRecord[136] && F[1]==K+0x155b55 && __readcr3()==XwnMapRecord[132];
    for(I=0;Valid && I<0x3c00;++I)for(J=0;J<6;++J)if(((PULONG)0xffb85000)[I*6+J]!=XwnPfnExpected[I][J]){Valid=FALSE;break;}
    for(I=0;Valid && I<1024;++I)if(C[I]!=XwnFreeColors[I])Valid=FALSE;
    for(I=0;I<4;++I)if(((PULONG)XwnMapRecord[209])[I]!=XwnFreeHead[I])Valid=FALSE;
    XwnMapRecord[280]=Valid;XwnMapRecord[264]=*(PULONG)(K+0x81bf8);
    for(I=0;I<2;++I){A=K+(I?0x75600:0x74ca0);P=(PULONG)A;
        for(J=0;J<0x108;++J){V=J==0?(I?2:0):J==7?K+0x6ca9c:J>=8?A+(J&~1UL)*4:0;if(P[J]!=V)Valid=FALSE;}}
    XwnMapRecord[268]=Valid;XwnMapRecord[269]=256;
    XwnMapRecord[281]=memcmp((PVOID)Process,XwnProcessBytes,sizeof(XwnProcessBytes))==0;
    XwnMapRecord[272]=*(PULONG)0xc0300c04;XwnMapRecord[273]=*(PULONG)0xc0301000;
    XwnMapRecord[270]=(XwnMapRecord[272]&~0x60UL)==((XwnMapRecord[262]<<12)|3);
    XwnMapRecord[271]=(XwnMapRecord[273]&~0x60UL)==((XwnMapRecord[263]<<12)|3);
    if(XwnMapRecord[270] && XwnMapRecord[271]){
        for(I=1;I<1024;++I)if(((PULONG)0xc0301000)[I])XwnMapRecord[270]=0;
        for(I=0;I<1024;++I)if(((PULONG)0xc0400000)[I])XwnMapRecord[271]=0;
    }
    XwnMapRecord[282]=*(PULONG)(K+0x755f0)==K+0x74ca0 && *(PULONG)(K+0x755f8)==K+0x75600 &&
        !*(PULONG)(K+0x7534c) && !*(PULONG)(K+0x6ca9c) &&
        *(PULONG)(K+0x81ab8)==0xc0301000 && *(PULONG)(K+0x81b90)==0xc03013fc &&
        *(PULONG)(K+0x82374)==0xc0501000 && *(PULONG)(K+0x81aa8)==0xc0501694;
    XwnMapRecord[274]=KeGetPcr()->Irql;XwnMapRecord[275]=__inbyte(0x21)|(__inbyte(0xa1)<<8);XwnMapRecord[276]=__readcr3();
    XwnMapRecord[278]=HalpXwnProcessMappings();XwnMapRecord[279]=XwnMapRecord[277]==XwnMapRecord[278];
    XwnMapRecord[261]=Valid && XwnMapRecord[264]+2==XwnMapRecord[210] && XwnMapRecord[281] &&
        XwnMapRecord[270] && XwnMapRecord[271] && XwnMapRecord[282] && XwnMapRecord[279] &&
        XwnMapRecord[274]==DISPATCH_LEVEL && XwnMapRecord[275]==0xffff && !KeGetPcr()->IRR &&
        KeGetPcr()->IDR==0xfffffffb && (__readeflags()&0x200) && HalpXwnDescriptorHash()==XwnMapRecord[144] &&
        *(PULONG)(XwnMapRecord[100]+12)==0x160 && *(PULONG)(XwnMapRecord[100]+16)==0x2000;
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    if(XwnMapRecord[261] && HalpXwnPrepareInit(Process)){
        ULONG Cr0=__readcr0();_disable();__writecr0(Cr0&~0x10000UL);
        RtlCopyMemory((PVOID)XwnProcessTarget,XwnProcessOriginal,5);__writecr0(Cr0);
        XwnMapRecord[290]=memcmp((PVOID)XwnProcessTarget,XwnProcessOriginal,5)==0;
        XwnMapRecord[291]=XwnMapRecord[290];if(XwnMapRecord[291])return;
    }
#endif
    HalpXwnMapCheckpoint(F);
}
#endif

#ifndef XBOX_NT5_PROCESSPAGES_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID NTAPI HalpXwnTailAfter(PULONG F,ULONG Largest)
{
    ULONG K=XwnMapRecord[6],I,J,A=0xc03e3000,Next,Size,N,Value,Count=0;BOOLEAN Valid;
    PULONG Pfn=(PULONG)0xffb85000,C=(PULONG)0xffbdf000;
    Valid=XwnMapRecord[240] && (ULONG_PTR)F==XwnMapRecord[136] && Largest==0x3f92bc &&
        __readcr3()==XwnMapRecord[132] && F[1]==K+0x155b55;
    for(I=0;Valid && I<0x3c00;++I)for(J=0;J<6;++J)if(Pfn[I*6+J]!=XwnPfnExpected[I][J]){Valid=FALSE;break;}
    for(I=0;Valid && I<1024;++I)if(C[I]!=XwnFreeColors[I])Valid=FALSE;
    XwnMapRecord[251]=Valid;
    for(I=0;I<4;++I)if(((PULONG)XwnMapRecord[209])[I]!=XwnFreeHead[I])Valid=FALSE;
    XwnMapRecord[249]=*(PULONG)(XwnMapRecord[100]+12)==0x160 && *(PULONG)(XwnMapRecord[100]+16)==0x2000 && HalpXwnDescriptorHash()==XwnMapRecord[144];
    for(I=5;I>0;--I){Size=XwnCacheSizes[I-1];N=XwnCacheCounts[I-1];Next=A+N*Size*4;
        if(*(PULONG)(K+0x81240+(I-1)*4)!=(((A-0xc0200000)/4)<<12) ||
           *(PULONG)(K+0x81220+(I-1)*4)!=Next-Size*4 || *(PULONG)(K+0x81280+(I-1)*4)!=N)Valid=FALSE;
        for(J=0;J<N*Size;++J){Value=0;
            if(J%Size==0)Value=(J/Size==N-1)?0xfffff000:(((A+(J+Size)*4-0xc0200000)/4)<<12);
            else if(J%Size==1)Value=0x2000;
            if(*(PULONG)(A+J*4)!=Value)Valid=FALSE;}
        Count+=N;A=Next;}
    if(A!=0xc03e4d60)Valid=FALSE;
    for(I=A;I<0xc03f92b8;I+=4){Value=I==A?0xfffff000:(I==A+4?0x5156000:0);if(*(PULONG)I!=Value)Valid=FALSE;}
    XwnMapRecord[252]=Valid;XwnMapRecord[243]=*(PULONG)(K+0x81bfc);XwnMapRecord[244]=(A-0xc03e3000)/4;XwnMapRecord[245]=Count;XwnMapRecord[246]=*(PULONG)(K+0x81218);
    XwnMapRecord[253]=*(PULONG)(K+0x6cae4)==0 && *(PULONG)(K+0x6cae8)==0 &&
        *(PULONG)(K+0x81258)==0xc03e3000 && *(PULONG)(K+0x81260)==0xc03f92b4 &&
        *(PULONG)(K+0x82398)==0x79358000 && *(PULONG)(K+0x81268)==3 && !*(PULONG)(K+0x81254) &&
        XwnMapRecord[243]==22702 && XwnMapRecord[246]==20822 &&
        *(PULONG)(K+0x81bf8)==XwnMapRecord[210] && HalpXwnEvents(TRUE);
    XwnMapRecord[248]=HalpXwnTailMappings();XwnMapRecord[242]=6;
    XwnMapRecord[241]=Valid && XwnMapRecord[249] && XwnMapRecord[253] &&
        XwnMapRecord[248]==XwnMapRecord[247] && KeGetPcr()->Irql==APC_LEVEL && !KeGetPcr()->IRR &&
        KeGetPcr()->IDR==0xfffffffb && (__readeflags()&0x200) && __inbyte(0x21)==0xff && __inbyte(0xa1)==0xff;
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
    if(XwnMapRecord[241] && HalpXwnPrepareProcess(F)){
        ULONG Cr0=__readcr0();_disable();__writecr0(Cr0&~0x10000UL);
        RtlCopyMemory((PVOID)XwnSysTarget,XwnSysOriginal,5);__writecr0(Cr0);
        XwnMapRecord[258]=memcmp((PVOID)XwnSysTarget,XwnSysOriginal,5)==0;
        XwnMapRecord[259]=XwnMapRecord[258];if(XwnMapRecord[259])return;
    }
#endif
    HalpXwnMapCheckpoint(F);
}
#endif

#ifndef XBOX_NT5_SYSPTES_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID NTAPI HalpXwnFreeAfter(PULONG Frame, ULONG Largest)
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
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
    if(XwnMapRecord[214] && HalpXwnPrepareTail(Frame)) {
        ULONG Cr0=__readcr0();_disable();__writecr0(Cr0&~0x10000UL);
        RtlCopyMemory((PVOID)XwnFreeTarget,XwnFreeOriginal,5);__writecr0(Cr0);
        XwnMapRecord[254]=memcmp((PVOID)XwnFreeTarget,XwnFreeOriginal,5)==0;
        XwnMapRecord[240]=XwnMapRecord[254];if(XwnMapRecord[240])return;
    }
#endif
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
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    UCHAR Expected[8]={0x83,0x7d,0xe4,0x01,0x75,0x6e,0xa1,0xb8};
    UCHAR ProcessExpected[8]={0xa1,0,0,0,0,0x89,0x06,0x89};
    static const UCHAR SysExpected[8]={0x6a,0,0x6a,0,0xe8,0x8c,0xb2,0xfe};
    static const UCHAR CommitExpected[8]={0x8b,0x45,0x08,0x8b,0x40,0x0c,0xe9,0x8e};
    UCHAR FreeExpected[8]={0x80,0x7d,0xfe,0,0x8b,0x15,0,0};
#elif defined(XBOX_NT5_PROCESSPAGES_PREFLIGHT)
    UCHAR Expected[8]={0xa1,0,0,0,0,0x89,0x06,0x89};
    static const UCHAR SysExpected[8]={0x6a,0,0x6a,0,0xe8,0x8c,0xb2,0xfe};
    static const UCHAR CommitExpected[8]={0x8b,0x45,0x08,0x8b,0x40,0x0c,0xe9,0x8e};
    UCHAR FreeExpected[8]={0x80,0x7d,0xfe,0,0x8b,0x15,0,0};
#elif defined(XBOX_NT5_SYSPTES_PREFLIGHT)
    UCHAR Expected[8]={0x6a,0,0x6a,0,0xe8,0x8c,0xb2,0xfe};
    static const UCHAR CommitExpected[8]={0x8b,0x45,0x08,0x8b,0x40,0x0c,0xe9,0x8e};
    UCHAR FreeExpected[8]={0x80,0x7d,0xfe,0,0x8b,0x15,0,0};
#elif defined(XBOX_NT5_FREELIST_PREFLIGHT)
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
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    *(PULONG)(ProcessExpected+1)=Seed[6]+0x73de8;
    *(PUSHORT)(FreeExpected+6)=(USHORT)(Seed[6]+0x81ab0);
    if(memcmp((PVOID)(Seed[6]+0x159ca0),ProcessExpected,8)||memcmp((PVOID)(Seed[6]+0x159bd7),SysExpected,8)||memcmp((PVOID)(Seed[6]+0x159898),FreeExpected,8)||memcmp((PVOID)(Seed[6]+0x1596f3),CommitExpected,8))return 0;
#elif defined(XBOX_NT5_PROCESSPAGES_PREFLIGHT)
    *(PULONG)(Expected+1)=Seed[6]+0x73de8;
    *(PUSHORT)(FreeExpected+6)=(USHORT)(Seed[6]+0x81ab0);
    if(memcmp((PVOID)(Seed[6]+0x159bd7),SysExpected,8) || memcmp((PVOID)(Seed[6]+0x159898),FreeExpected,8) || memcmp((PVOID)(Seed[6]+0x1596f3),CommitExpected,8))return 0;
#elif defined(XBOX_NT5_SYSPTES_PREFLIGHT)
    *(PUSHORT)(FreeExpected+6)=(USHORT)(Seed[6]+0x81ab0);
    if(memcmp((PVOID)(Seed[6]+0x159898),FreeExpected,8) || memcmp((PVOID)(Seed[6]+0x1596f3),CommitExpected,8))return 0;
#elif defined(XBOX_NT5_FREELIST_PREFLIGHT)
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
#ifdef XBOX_NT5_SYSPTES_PREFLIGHT
    XwnFreeTarget=Seed[6]+0x159898;RtlCopyMemory(XwnFreeOriginal,(PVOID)XwnFreeTarget,5);
    *(PUCHAR)XwnFreeTarget=0xe9;*(PULONG)(XwnFreeTarget+1)=(ULONG_PTR)HalpXwnFreeEntry-XwnFreeTarget-5;
    XwnMapRecord[238]=XwnFreeTarget;XwnMapRecord[239]=(ULONG_PTR)HalpXwnFreeEntry;
#endif
#ifdef XBOX_NT5_PROCESSPAGES_PREFLIGHT
    XwnSysTarget=Seed[6]+0x159bd7;RtlCopyMemory(XwnSysOriginal,(PVOID)XwnSysTarget,5);
    *(PUCHAR)XwnSysTarget=0xe9;*(PULONG)(XwnSysTarget+1)=(ULONG_PTR)HalpXwnSysEntry-XwnSysTarget-5;
    XwnMapRecord[256]=XwnSysTarget;XwnMapRecord[257]=(ULONG_PTR)HalpXwnSysEntry;
#endif
#ifdef XBOX_NT5_PROCESSINIT_PREFLIGHT
    XwnProcessTarget=Seed[6]+0x159ca0;RtlCopyMemory(XwnProcessOriginal,(PVOID)XwnProcessTarget,5);
    *(PUCHAR)XwnProcessTarget=0xe9;*(PULONG)(XwnProcessTarget+1)=(ULONG_PTR)HalpXwnProcessEntry-XwnProcessTarget-5;
    XwnMapRecord[288]=XwnProcessTarget;XwnMapRecord[289]=(ULONG_PTR)HalpXwnProcessEntry;
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
