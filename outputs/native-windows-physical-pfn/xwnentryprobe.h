/* Explicit early-kernel diagnostic. Included only in the opt-in rosload. */
#ifdef XBOX_NATIVE_FATX_PHASE0_PREFLIGHT
#if defined(XBOX_NATIVE_FATX_PFN_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x5a4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x50464e54
#define XWN_ARM_REPLY 0x50464854
#elif defined(XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x4a4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x50494e54
#define XWN_ARM_REPLY 0x50494854
#elif defined(XBOX_NATIVE_FATX_POOL_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x454e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x504f4e54
#define XWN_ARM_REPLY 0x504f4854
#elif defined(XBOX_NATIVE_FATX_PT_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x4c4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x50544E54
#define XWN_ARM_REPLY 0x50544854
#elif defined(XBOX_NATIVE_FATX_SIZE_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x4a4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x535A4E54
#define XWN_ARM_REPLY 0x535A4854
#elif defined(XBOX_NATIVE_FATX_SCAN_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x5a4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x53434E54
#define XWN_ARM_REPLY 0x53434854
#elif defined(XBOX_NATIVE_FATX_MAP_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x594e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x4D504E54
#define XWN_ARM_REPLY 0x4D504854
#elif defined(XBOX_NATIVE_FATX_MI_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x444e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x4D494E54
#define XWN_ARM_REPLY 0x4D494854
#elif defined(XBOX_NATIVE_FATX_MM_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x4d4e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x4D4D4E54
#define XWN_ARM_REPLY 0x4D4D4854
#elif defined(XBOX_NATIVE_FATX_BIOS_PREFLIGHT)
static volatile ULONG XwnEntryRecord[96] = {0x494e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x42494E54
#define XWN_ARM_REPLY 0x42494854
#elif defined(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT)
static volatile ULONG XwnEntryRecord[80] = {0x524e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x52474E54
#define XWN_ARM_REPLY 0x52474854
#elif defined(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT)
static volatile ULONG XwnEntryRecord[80] = {0x434e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x434C4E54
#define XWN_ARM_REPLY 0x434C4854
#elif defined(XBOX_NATIVE_FATX_TIMER_PREFLIGHT)
static volatile ULONG XwnEntryRecord[64] = {0x544e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x54494E54
#define XWN_ARM_REPLY 0x54494854
#elif defined(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
static volatile ULONG XwnEntryRecord[48] = {0x424e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x42414E54
#define XWN_ARM_REPLY 0x42414854
#else
static volatile ULONG XwnEntryRecord[36] = {0x304e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x50304E54
#define XWN_ARM_REPLY 0x50304854
#endif
#include "xwnphase0callback.h"
#else
static volatile ULONG XwnEntryRecord[24] = {0x454e5758, 0x35544e50, 1, 0};
#define XWN_ARM_SIGNATURE 0x58454E54
#define XWN_ARM_REPLY 0x58484C54

static DECLSPEC_NORETURN VOID NTAPI
XwnFirstHalCheckpoint(ULONG Processor, PLOADER_PARAMETER_BLOCK LoaderBlock,
                      PVOID Caller)
{
    CHAR Text[128];
    BOOLEAN Valid;
    _disable();
    XwnEntryRecord[12] = Processor;
    XwnEntryRecord[13] = (ULONG_PTR)LoaderBlock;
    XwnEntryRecord[14] = (ULONG_PTR)Caller;
    XwnEntryRecord[15] = __readcr0();
    XwnEntryRecord[16] = __readcr3();
    Valid = XwnEntryRecord[3] == 30 && Processor == 0 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller >= XwnEntryRecord[6] &&
            (ULONG_PTR)Caller - XwnEntryRecord[6] < XwnEntryRecord[7] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11];
    XwnEntryRecord[3] = Valid ? 90 : 40;
    XwnPagingClear();
    XwnPagingText(4, "XWN Windows 2000 first HAL checkpoint", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNK90: Windows kernel reached first HAL checkpoint."
                          : "XWNKFAIL: First HAL checkpoint validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "CPU: %lu  Caller: %08lx  Loader: %08lx",
                      Processor, (ULONG_PTR)Caller, (ULONG_PTR)LoaderBlock);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "CR0: %08lx  CR3: %08lx", __readcr0(), __readcr3());
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE original HAL processor initialization.", 0xFFFFFFFF);
    XwnPagingText(17, "Boot-driver entry and Windows desktop NOT reached.", 0xFFFFFFFF);
    XwnPagingText(20, "Photograph this screen, then reboot to the dashboard.", 0xFFFFFFFF);
    for (;;) __halt();
}

#endif /* XBOX_NATIVE_FATX_PHASE0_PREFLIGHT */

#if defined(XBOX_NATIVE_FATX_MAP_PREFLIGHT)
/* The post-unmap checkpoint executes entirely in the high HAL. */
#elif defined(XBOX_NATIVE_FATX_MI_PREFLIGHT)
static PUCHAR XwnMiTarget;
static UCHAR XwnMiOriginal[10];

static DECLSPEC_NORETURN VOID NTAPI
XwnMiCheckpoint(PLOADER_PARAMETER_BLOCK LoaderBlock)
{
    const ULONG Phase = 0, Context = 0;
    ULONG Flags = __readeflags(), Cr0 = __readcr0();
    BOOLEAN Valid;
    CHAR Text[128];
    PVOID Caller = _ReturnAddress();
    _disable();
    Valid = XwnMiTarget && XwnEntryRecord[3] == 30 && XwnEntryRecord[24] == 80 &&
            Phase == 0 && (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[6] + 0x155b55 &&
            (Cr0 & 0x80000000) && __readcr3() == XwnEntryRecord[11];
    if (XwnMiTarget)
    {
        __writecr0(Cr0 & ~0x10000);
        RtlCopyMemory(XwnMiTarget, XwnMiOriginal, sizeof(XwnMiOriginal));
        __writecr0(Cr0);
        XwnEntryRecord[87] = memcmp(XwnMiTarget, XwnMiOriginal, sizeof(XwnMiOriginal)) == 0;
    }
    Valid = Valid && XwnEntryRecord[87];
    XwnEntryRecord[81] = Phase;
    XwnEntryRecord[82] = (ULONG_PTR)LoaderBlock;
    XwnEntryRecord[83] = (ULONG_PTR)Caller;
    XwnEntryRecord[84] = Cr0;
    XwnEntryRecord[85] = __readcr3();
    XwnEntryRecord[86] = Flags;
    XwnEntryRecord[89] = Context;
    XwnEntryRecord[24] = 90;
    XwnEntryRecord[3] = Valid ? 90 : 40;
    XwnPagingClear();
    XwnPagingText(4, "XWN Windows 2000 machine-dependent MM entry", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWND90: MM prefix completed; machine init reached."
                          : "XWNDFAIL: Machine-init checkpoint failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Phase: %lu  Loader: %08lx  Caller: %08lx",
                      Phase, (ULONG_PTR)LoaderBlock, (ULONG_PTR)Caller);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "CR3: %08lx  Entry bytes restored: %lu",
                      __readcr3(), XwnEntryRecord[87]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE MiInitMachineDependent body.", 0xFFFFFFFF);
    XwnPagingText(17, "Partition calls, boot drivers and desktop NOT reached.", 0xFFFFFFFF);
    XwnPagingText(20, "Photograph this screen, then reboot to the dashboard.", 0xFFFFFFFF);
    for (;;) __halt();
}

static BOOLEAN XwnArmMiCheckpoint(PLDR_DATA_TABLE_ENTRY Kernel)
{
    static const UCHAR Expected[14] = {
        0x55,0x8b,0xec,0x83,0xec,0x68,0x80,0x65,0xfe,0,0x53,0x56,0x33,0xf6};
    PIMAGE_NT_HEADERS Nt = RtlImageNtHeader(Kernel->DllBase);
    PUCHAR Target = (PUCHAR)Kernel->DllBase + 0x157d78;
    ULONG Cr0;
    if (!Nt || Nt->FileHeader.TimeDateStamp != 1266293717 ||
        Nt->OptionalHeader.CheckSum != 1747402 ||
        Kernel->SizeOfImage != 1691648 || Nt->OptionalHeader.AddressOfEntryPoint != 44560 ||
        memcmp(Target, Expected, sizeof(Expected))) return FALSE;
    XwnMiTarget = Target;
    RtlCopyMemory(XwnMiOriginal, Target, sizeof(XwnMiOriginal));
    Cr0 = __readcr0();
    _disable();
    __writecr0(Cr0 & ~0x10000);
    Target[0] = 0xe9;
    *(PULONG)(Target + 1) = (ULONG_PTR)XwnMiCheckpoint - (ULONG_PTR)(Target + 5);
    RtlFillMemory(Target + 5, 5, 0x90);
    __writecr0(Cr0);
    XwnEntryRecord[80] = (ULONG_PTR)Target;
    XwnEntryRecord[88] = (ULONG_PTR)XwnMiCheckpoint;
    return TRUE;
}
#elif defined(XBOX_NATIVE_FATX_MM_PREFLIGHT)
static PUCHAR XwnMmTarget;
static UCHAR XwnMmOriginal[9];

static DECLSPEC_NORETURN VOID NTAPI
XwnMmCheckpoint(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, ULONG Context)
{
    ULONG Flags = __readeflags(), Cr0 = __readcr0();
    BOOLEAN Valid;
    CHAR Text[128];
    PVOID Caller = _ReturnAddress();
    _disable();
    Valid = XwnMmTarget && XwnEntryRecord[3] == 30 && XwnEntryRecord[24] == 80 &&
            Phase == 0 && (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[6] + 0x147f95 &&
            (Cr0 & 0x80000000) && __readcr3() == XwnEntryRecord[11];
    if (XwnMmTarget)
    {
        __writecr0(Cr0 & ~0x10000);
        RtlCopyMemory(XwnMmTarget, XwnMmOriginal, sizeof(XwnMmOriginal));
        __writecr0(Cr0);
        XwnEntryRecord[87] = memcmp(XwnMmTarget, XwnMmOriginal, sizeof(XwnMmOriginal)) == 0;
    }
    Valid = Valid && XwnEntryRecord[87];
    XwnEntryRecord[81] = Phase;
    XwnEntryRecord[82] = (ULONG_PTR)LoaderBlock;
    XwnEntryRecord[83] = (ULONG_PTR)Caller;
    XwnEntryRecord[84] = Cr0;
    XwnEntryRecord[85] = __readcr3();
    XwnEntryRecord[86] = Flags;
    XwnEntryRecord[89] = Context;
    XwnEntryRecord[24] = 90;
    XwnEntryRecord[3] = Valid ? 90 : 40;
    XwnPagingClear();
    XwnPagingText(4, "XWN Windows 2000 memory-manager entry", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNM90: HAL returned; memory-manager entry reached."
                          : "XWNMFAIL: Memory-manager checkpoint failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Phase: %lu  Loader: %08lx  Caller: %08lx",
                      Phase, (ULONG_PTR)LoaderBlock, (ULONG_PTR)Caller);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "CR3: %08lx  Entry bytes restored: %lu",
                      __readcr3(), XwnEntryRecord[87]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE the original MmInitSystem body.", 0xFFFFFFFF);
    XwnPagingText(17, "Partition calls, boot drivers and desktop NOT reached.", 0xFFFFFFFF);
    XwnPagingText(20, "Photograph this screen, then reboot to the dashboard.", 0xFFFFFFFF);
    for (;;) __halt();
}

static BOOLEAN XwnArmMmCheckpoint(PLDR_DATA_TABLE_ENTRY Kernel)
{
    static const UCHAR Expected[24] = {
        0x55,0x8b,0xec,0x81,0xec,0xf0,0,0,0,0x53,0x33,0xdb,
        0x39,0x5d,0x08,0x56,0x57,0x0f,0x85,0xa4,0x0e,0,0,0x8b};
    PIMAGE_NT_HEADERS Nt = RtlImageNtHeader(Kernel->DllBase);
    PUCHAR Target = (PUCHAR)Kernel->DllBase + 0x15542c;
    ULONG Cr0;
    if (!Nt || Nt->FileHeader.TimeDateStamp != 1266293717 ||
        Nt->OptionalHeader.CheckSum != 1747402 ||
        Kernel->SizeOfImage != 1691648 || Nt->OptionalHeader.AddressOfEntryPoint != 44560 ||
        memcmp(Target, Expected, sizeof(Expected))) return FALSE;
    XwnMmTarget = Target;
    RtlCopyMemory(XwnMmOriginal, Target, sizeof(XwnMmOriginal));
    Cr0 = __readcr0();
    _disable();
    __writecr0(Cr0 & ~0x10000);
    Target[0] = 0xe9;
    *(PULONG)(Target + 1) = (ULONG_PTR)XwnMmCheckpoint - (ULONG_PTR)(Target + 5);
    RtlFillMemory(Target + 5, 4, 0x90);
    __writecr0(Cr0);
    XwnEntryRecord[80] = (ULONG_PTR)Target;
    XwnEntryRecord[88] = (ULONG_PTR)XwnMmCheckpoint;
    return TRUE;
}
#endif

/* The loaded image is already PE-validated. Reject malformed export extents. */
static PVOID XwnFindHalExport(PLDR_DATA_TABLE_ENTRY Module, PCSTR Name)
{
    PUCHAR Base = Module->DllBase;
    PIMAGE_NT_HEADERS Nt = RtlImageNtHeader(Base);
    PIMAGE_EXPORT_DIRECTORY Ex;
    ULONG Rva, Size, I, *Names, *Functions;
    PUSHORT Ordinals;
    if (!Nt) return NULL;
    Rva = Nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
    Size = Nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Size;
    if (!Rva || Size < sizeof(*Ex) || Rva >= Module->SizeOfImage ||
        Size > Module->SizeOfImage - Rva) return NULL;
    Ex = (PIMAGE_EXPORT_DIRECTORY)(Base + Rva);
    if (Ex->NumberOfNames > 4096 || Ex->NumberOfFunctions > 4096 ||
        Ex->AddressOfNames >= Module->SizeOfImage ||
        Ex->NumberOfNames * 4 > Module->SizeOfImage - Ex->AddressOfNames ||
        Ex->AddressOfNameOrdinals >= Module->SizeOfImage ||
        Ex->NumberOfNames * 2 > Module->SizeOfImage - Ex->AddressOfNameOrdinals ||
        Ex->AddressOfFunctions >= Module->SizeOfImage ||
        Ex->NumberOfFunctions * 4 > Module->SizeOfImage - Ex->AddressOfFunctions) return NULL;
    Names = (PULONG)(Base + Ex->AddressOfNames);
    Ordinals = (PUSHORT)(Base + Ex->AddressOfNameOrdinals);
    Functions = (PULONG)(Base + Ex->AddressOfFunctions);
    for (I = 0; I < Ex->NumberOfNames; ++I)
    {
        ULONG Length = (ULONG)strlen(Name) + 1, Function;
        if (Names[I] >= Module->SizeOfImage || Length > Module->SizeOfImage - Names[I]) continue;
        if (memcmp(Base + Names[I], Name, Length)) continue;
        if (Ordinals[I] >= Ex->NumberOfFunctions) return NULL;
        Function = Functions[Ordinals[I]];
        if (!Function || Function >= Module->SizeOfImage ||
            (Function >= Rva && Function - Rva < Size)) return NULL;
        return Base + Function;
    }
    return NULL;
}

static DECLSPEC_NORETURN VOID XwnEnterKernelProbe(PLOADER_PARAMETER_BLOCK LoaderBlock)
{
    PLIST_ENTRY Link;
    PLDR_DATA_TABLE_ENTRY Hal = NULL, Kernel = NULL;
    ULONG Count = 0;
    typedef ULONG (NTAPI *CONFIGURE)(PVOID, ULONG);
    CONFIGURE Configure = NULL;
    for (Link = LoaderBlock->LoadOrderListHead.Flink;
         Link != &LoaderBlock->LoadOrderListHead && Count++ < 64; Link = Link->Flink)
    {
        PLDR_DATA_TABLE_ENTRY M = CONTAINING_RECORD(Link, LDR_DATA_TABLE_ENTRY, InLoadOrderLinks);
        if (M->BaseDllName.Length == 14 && !_wcsnicmp(M->BaseDllName.Buffer, L"hal.dll", 7)) Hal = M;
        if (M->BaseDllName.Length == 24 && !_wcsnicmp(M->BaseDllName.Buffer, L"ntoskrnl.exe", 12)) Kernel = M;
    }
    if (Hal && Kernel && Count < 64)
        Configure = (CONFIGURE)XwnFindHalExport(Hal, "XwnConfigureEntryProbe");
    if (!Configure || Configure(XwnFirstHalCheckpoint, XWN_ARM_SIGNATURE) != XWN_ARM_REPLY)
    {
        XwnEntryRecord[3] = 40;
        XwnEntryRecord[22] = 1;
        XwnPagingClear();
        XwnPagingText(7, "XWNKFAIL: Required halt-only HAL was not armed.", 0xFFFF0000);
        XwnPagingText(11, "Windows kernel NOT entered. Photograph, then reboot.", 0xFFFFFFFF);
        _disable(); for (;;) __halt();
    }
    XwnEntryRecord[4] = (ULONG_PTR)LoaderBlock;
    XwnEntryRecord[5] = XwnHandoffRecord[6];
    XwnEntryRecord[6] = (ULONG_PTR)Kernel->DllBase;
    XwnEntryRecord[7] = Kernel->SizeOfImage;
    XwnEntryRecord[8] = (ULONG_PTR)Hal->DllBase;
    XwnEntryRecord[9] = (ULONG_PTR)Configure;
    XwnEntryRecord[10] = (ULONG_PTR)XwnFirstHalCheckpoint;
    XwnEntryRecord[11] = __readcr3();
    XwnEntryRecord[17] = XwnDisplayWidth;
    XwnEntryRecord[18] = XwnDisplayHeight;
    XwnEntryRecord[19] = XwnDisplayPitch;
    XwnEntryRecord[20] = XwnPagingFramebuffer;
    XwnEntryRecord[21] = XwnFramebufferBytes;
    XwnEntryRecord[23] = (ULONG_PTR)XwnFindHalExport(Hal, "HalInitSystem");
#ifdef XBOX_NATIVE_FATX_MM_PREFLIGHT
#ifdef XBOX_NATIVE_FATX_MAP_PREFLIGHT
    {
    CONFIGURE ArmMap = (CONFIGURE)XwnFindHalExport(Hal, "XwnConfigureMapProbe");
    if (!ArmMap || ArmMap((PVOID)XwnEntryRecord, XWN_ARM_SIGNATURE) != XWN_ARM_REPLY)
#elif defined(XBOX_NATIVE_FATX_MI_PREFLIGHT)
    if (!XwnArmMiCheckpoint(Kernel))
#else
    if (!XwnArmMmCheckpoint(Kernel))
#endif
    {
        XwnEntryRecord[3] = 40;
        XwnEntryRecord[22] = 3;
        XwnPagingClear();
        XwnPagingText(7, "XWNMFAIL: Pinned kernel checkpoint bytes do not match.", 0xFFFF0000);
        _disable(); for (;;) __halt();
    }
#ifdef XBOX_NATIVE_FATX_MAP_PREFLIGHT
    }
#endif
#endif
    XwnPagingClear();
#if defined(XBOX_NATIVE_FATX_PFN_PREFLIGHT)
    XwnPagingText(7, "XWNE30: Entering Windows; PFN-backing stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_POOLINIT_PREFLIGHT)
    XwnPagingText(7, "XWNU30: Entering Windows; pool-initialization stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_POOL_PREFLIGHT)
    XwnPagingText(7, "XWNO30: Entering Windows; pool-mapping stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_PT_PREFLIGHT)
    XwnPagingText(7, "XWNA30: Entering Windows; first page-table stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_SIZE_PREFLIGHT)
    XwnPagingText(7, "XWNQ30: Entering Windows; sizing stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_SCAN_PREFLIGHT)
    XwnPagingText(7, "XWNS30: Entering Windows; RAM-scan stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_MAP_PREFLIGHT)
    XwnPagingText(7, "XWNV30: Entering Windows; high HAL stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_MI_PREFLIGHT)
    XwnPagingText(7, "XWND30: Entering Windows; machine-init stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_MM_PREFLIGHT)
    XwnPagingText(7, "XWNM30: Entering Windows; memory-manager stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_BIOS_PREFLIGHT)
    XwnPagingText(7, "XWNI30: Entering Windows; post-BIOS halt armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT)
    XwnPagingText(7, "XWNR30: Entering Windows; partition-hook stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT)
    XwnPagingText(7, "XWNC30: Entering Windows; pre-storage stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_TIMER_PREFLIGHT)
    XwnPagingText(7, "XWNT30: Entering Windows; post-calibration stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
    XwnPagingText(7, "XWNB30: Entering Windows; pre-timer HAL stop armed.", 0xFFFFFF00);
#elif defined(XBOX_NATIVE_FATX_PHASE0_PREFLIGHT)
    XwnPagingText(7, "XWNH30: Entering Windows; HAL phase-0 stop armed.", 0xFFFFFF00);
#else
    XwnPagingText(7, "XWNK30: Entering Windows; first HAL checkpoint armed.", 0xFFFFFF00);
#endif
    XwnPagingText(11, "If this remains, kernel entry has NOT been confirmed.", 0xFFFFFFFF);
    XwnEntryRecord[3] = 30;
    ((KERNEL_ENTRY_POINT)XwnEntryRecord[5])(LoaderBlock);
    XwnEntryRecord[3] = 40;
    XwnEntryRecord[22] = 2;
    _disable(); for (;;) __halt();
}
