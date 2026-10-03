/* Explicit early-kernel diagnostic. Included only in the opt-in rosload. */
#ifdef XBOX_NATIVE_FATX_PHASE0_PREFLIGHT
#ifdef XBOX_NATIVE_FATX_HALBASE_PREFLIGHT
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
    XwnPagingClear();
#if defined(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
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
