/* The opt-in phase-0 probe returns only for the two processor checkpoints. */
static ULONG NTAPI
XwnFirstHalCheckpoint(ULONG Stage, PLOADER_PARAMETER_BLOCK LoaderBlock,
                      PVOID Caller, PULONG State)
{
    BOOLEAN Valid;
    CHAR Text[128];
    _disable();
    Valid = XwnEntryRecord[3] == 30 && State &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller >= XwnEntryRecord[6] &&
            (ULONG_PTR)Caller - XwnEntryRecord[6] < XwnEntryRecord[7] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11];
    if (Valid && Stage == 10 && XwnEntryRecord[24] == 0 && State[0] == 0)
    {
        XwnEntryRecord[24] = 10;
        XwnEntryRecord[26] = (ULONG_PTR)Caller;
        return 0x50524330;
    }
    if (Valid && Stage == 20 && XwnEntryRecord[24] == 10 && State[0] == 0 &&
        State[1] == 0xFFFFFFFB && State[2] == 100 && State[3] == 1 && State[4] == 1)
    {
        XwnEntryRecord[24] = 20;
        XwnEntryRecord[25] = 1;
        XwnEntryRecord[27] = (ULONG_PTR)Caller;
        XwnEntryRecord[28] = State[1];
        XwnEntryRecord[29] = State[2];
        XwnEntryRecord[30] = State[3];
        XwnEntryRecord[31] = State[4];
        return 0x50524330;
    }
    Valid = Valid && Stage == 30 && XwnEntryRecord[24] == 20 &&
            XwnEntryRecord[25] == 1 && State[0] == 0;
#ifdef XBOX_NATIVE_FATX_HALBASE_PREFLIGHT
    if (Valid)
    {
        XwnEntryRecord[24] = 30;
        XwnEntryRecord[45] = (ULONG_PTR)Caller;
        return 0x50524330;
    }
    Valid = XwnEntryRecord[3] == 30 && State && Stage == 40 &&
            XwnEntryRecord[24] == 30 && XwnEntryRecord[25] == 1 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[45] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11] &&
            State[0] == 0 && State[5] == 1 && State[6] == State[7] &&
            State[8] == 0x1800 && State[9] == 0xffff && State[10] == 50 &&
            State[11] == 0x7f && (State[12] & 0x200) && State[13] == 0;
    if (Stage == 40 && State)
    {
        ULONG I;
        for (I = 0; I < 9; ++I) XwnEntryRecord[36 + I] = State[5 + I];
    }
#endif
#ifdef XBOX_NATIVE_FATX_TIMER_PREFLIGHT
    if (Valid && Stage == 40)
    {
        XwnEntryRecord[24] = 40;
        XwnPagingClear();
        XwnPagingText(4, "XWN Windows 2000 RTC timer calibration", 0xFFFFFFFF);
        XwnPagingText(7, "XWNT40: Base HAL passed; starting RTC calibration.", 0xFFFFFF00);
        XwnPagingText(11, "Waiting for RTC interrupts; completion NOT confirmed.", 0xFFFFFFFF);
        XwnPagingText(15, "If unchanged after 15 seconds, photograph then reboot.", 0xFFFFFFFF);
        return 0x50524330;
    }
    Valid = XwnEntryRecord[3] == 30 && State && Stage == 50 &&
            XwnEntryRecord[24] == 40 && XwnEntryRecord[25] == 1 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[45] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11] &&
            State[0] == 0 && State[2] > 0 && State[2] <= 1000000 &&
            State[5] == State[8] && State[6] == State[9] && State[7] == State[10] &&
            State[11] == 0xffff && (State[12] & 0x200);
    if (State && Stage == 50)
    {
        ULONG I;
        for (I = 0; I < 8; ++I) XwnEntryRecord[46 + I] = State[5 + I];
        XwnEntryRecord[54] = State[2];
    }
#endif
#ifdef XBOX_NATIVE_FATX_CLOCK_PREFLIGHT
    if (Valid && Stage == 50)
    {
        XwnEntryRecord[24] = 50;
        XwnPagingClear();
        XwnPagingText(4, "XWN Windows 2000 clock setup", 0xFFFFFFFF);
        XwnPagingText(7, "XWNC50: RTC calibration passed; configuring clock.", 0xFFFFFF00);
        XwnPagingText(12, "Clock completion NOT confirmed; storage NOT entered.", 0xFFFFFFFF);
        return 0x50524330;
    }
    Valid = XwnEntryRecord[3] == 30 && State && Stage == 60 &&
            XwnEntryRecord[24] == 50 && XwnEntryRecord[25] == 1 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[45] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11] &&
            State[0] == 0 && State[2] == XwnEntryRecord[54] &&
            State[5] == 16875 && State[6] == 150000 && State[7] == 15 &&
            State[8] == State[5] && State[9] == State[6] && State[10] == 1 &&
            State[11] == 0xffff && (State[12] & 0x200) && !(State[13] & 0x40) &&
            State[14] <= State[5] && State[15] == 10000;
    if (State && Stage == 60)
    {
        ULONG I;
        for (I = 0; I < 11; ++I) XwnEntryRecord[55 + I] = State[5 + I];
    }
#endif
#ifdef XBOX_NATIVE_FATX_HOOKS_PREFLIGHT
    if (Valid && Stage == 60)
    {
        XwnEntryRecord[24] = 60;
        return 0x50524330;
    }
    Valid = XwnEntryRecord[3] == 30 && State && Stage == 70 &&
            XwnEntryRecord[24] == 60 && XwnEntryRecord[25] == 1 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[45] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11] &&
            State[0] == 0 && State[1] == 0xFFFFFFFB && State[2] == XwnEntryRecord[54] &&
            State[3] == 1 && State[4] == 1 && State[5] == 15 && State[6] == 15 &&
            State[7] == 0xffff && (State[8] & 0x200);
    if (State && Stage == 70)
    {
        ULONG I;
        for (I = 0; I < 4; ++I) XwnEntryRecord[66 + I] = State[5 + I];
    }
#endif
#ifdef XBOX_NATIVE_FATX_BIOS_PREFLIGHT
    if (Valid && Stage == 70)
    {
        XwnEntryRecord[24] = 70;
        return 0x50524330;
    }
    Valid = XwnEntryRecord[3] == 30 && State && Stage == 80 &&
            XwnEntryRecord[24] == 70 && XwnEntryRecord[25] == 1 &&
            (ULONG_PTR)LoaderBlock == XwnEntryRecord[4] &&
            (ULONG_PTR)Caller == XwnEntryRecord[45] &&
            (__readcr0() & 0x80000000) && __readcr3() == XwnEntryRecord[11] &&
            State[0] == 0 && State[1] == 0xFFFFFFFB && State[2] == XwnEntryRecord[54] &&
            State[3] == 1 && State[4] == 1 && State[5] > 0 && State[5] < 0x100 &&
            State[6] > 0 && State[6] < 0x100000 && !(State[6] & 0xfff) &&
            State[5] != (State[6] >> 12) && State[7] == 0 &&
            State[8] > 0 && State[8] < 128 && State[9] == 2 &&
            State[10] == 0xffff && (State[11] & 0x200) && State[12] == 0 &&
            State[13] == 3 && State[14] == 1;
    if (State && Stage == 80)
    {
        ULONG I;
        for (I = 0; I < 10; ++I) XwnEntryRecord[70 + I] = State[5 + I];
    }
#endif
    XwnEntryRecord[12] = State ? State[0] : ~0;
    XwnEntryRecord[13] = (ULONG_PTR)LoaderBlock;
    XwnEntryRecord[14] = (ULONG_PTR)Caller;
    XwnEntryRecord[15] = __readcr0();
    XwnEntryRecord[16] = __readcr3();
    if (State)
    {
        XwnEntryRecord[32] = State[1];
        XwnEntryRecord[33] = State[2];
        XwnEntryRecord[34] = State[3];
        XwnEntryRecord[35] = State[4];
    }
    XwnEntryRecord[24] = Stage;
    XwnEntryRecord[3] = Valid ? 90 : 40;
    XwnPagingClear();
#if defined(XBOX_NATIVE_FATX_BIOS_PREFLIGHT)
    XwnPagingText(4, "XWN Windows 2000 BIOS phase-0 allocation", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNI90: BIOS pages reserved; HAL return blocked."
                          : "XWNIFAIL: BIOS allocation validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Fallback PFN: %08lx  Buffer PA: %08lx",
                      XwnEntryRecord[70], XwnEntryRecord[71]);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "Descriptors: %lu  Allocations: %lu  Reserved: %lx/3",
                      XwnEntryRecord[73], XwnEntryRecord[74], XwnEntryRecord[78]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "PIC: %04lx  Stall: %lu  Stage: %lu",
                      XwnEntryRecord[75], XwnEntryRecord[54], Stage);
    XwnPagingText(14, Text, 0xFFFFFFFF);
    XwnPagingText(16, "HAL phase-0 body finished; return to kernel blocked.", 0xFFFFFFFF);
    XwnPagingText(18, "Partition calls, boot drivers and desktop NOT reached.", 0xFFFFFFFF);
#elif defined(XBOX_NATIVE_FATX_HOOKS_PREFLIGHT)
    XwnPagingText(4, "XWN Windows 2000 partition-hook registration", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNR90: Partition hooks registered; no disk access."
                          : "XWNRFAIL: Partition-hook validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Installed hooks: %lx/0f  Saved originals: %lx/0f",
                      XwnEntryRecord[66], XwnEntryRecord[67]);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "PIC: %04lx  Stall factor: %lu  Stage: %lu",
                      XwnEntryRecord[68], XwnEntryRecord[54], Stage);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE BIOS allocation and partition calls.", 0xFFFFFFFF);
    XwnPagingText(17, "Boot-driver entry and Windows desktop NOT reached.", 0xFFFFFFFF);
#elif defined(XBOX_NATIVE_FATX_CLOCK_PREFLIGHT)
    XwnPagingText(4, "XWN Windows 2000 clock setup", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNC90: Clock configured; stopped before storage."
                          : "XWNCFAIL: Clock state validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Increment: %lu x100ns  PIT reload: %lu",
                      XwnEntryRecord[56], XwnEntryRecord[55]);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "PIC: %04lx  RTC B: %02lx  Profile stopped: %lu",
                      XwnEntryRecord[61], XwnEntryRecord[63], XwnEntryRecord[60]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "PIT count snapshot: %lu  Stall factor: %lu",
                      XwnEntryRecord[64], XwnEntryRecord[54]);
    XwnPagingText(14, Text, 0xFFFFFFFF);
    XwnPagingText(17, "Storage, boot-driver entry and desktop NOT reached.", 0xFFFFFFFF);
#elif defined(XBOX_NATIVE_FATX_TIMER_PREFLIGHT)
    XwnPagingText(4, "XWN Windows 2000 RTC timer calibration", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNT90: RTC calibration returned; interrupt state restored."
                          : "XWNTFAIL: RTC calibration state validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Stall factor: %lu  PIC mask: %04lx  EFLAGS: %08lx",
                      XwnEntryRecord[54], XwnEntryRecord[52], XwnEntryRecord[53]);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "RTC IDT before: %08lx %08lx",
                      XwnEntryRecord[46], XwnEntryRecord[47]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "RTC IDT after:  %08lx %08lx",
                      XwnEntryRecord[49], XwnEntryRecord[50]);
    XwnPagingText(14, Text, 0xFFFFFFFF);
    XwnPagingText(17, "Stopped BEFORE clock setup, storage and boot drivers.", 0xFFFFFFFF);
#elif defined(XBOX_NATIVE_FATX_HALBASE_PREFLIGHT)
    XwnPagingText(4, "XWN Windows 2000 base HAL initialization", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNB90: Base HAL checks and PIC setup completed."
                          : "XWNBFAIL: Base HAL checkpoint validation failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "PRCB: %lu  Build: %lu/%lu  ELCR: %04lx",
                      XwnEntryRecord[36], XwnEntryRecord[37], XwnEntryRecord[38], XwnEntryRecord[39]);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "PIC mask: %04lx  CMOS: %lu  Dispatch: %02lx",
                      XwnEntryRecord[40], XwnEntryRecord[41], XwnEntryRecord[42]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE timer calibration and storage setup.", 0xFFFFFFFF);
    XwnPagingText(17, "Boot-driver entry and Windows desktop NOT reached.", 0xFFFFFFFF);
#else
    XwnPagingText(4, "XWN Windows 2000 HAL phase-0 boundary", 0xFFFFFFFF);
    XwnPagingText(7, Valid ? "XWNH90: Processor initialized; HAL phase 0 reached."
                          : "XWNHFAIL: HAL checkpoint sequence or state failed.",
                  Valid ? 0xFF00FF00 : 0xFFFF0000);
    RtlStringCbPrintfA(Text, sizeof(Text), "Stage: %lu  Phase/CPU: %lu  Caller: %08lx",
                      Stage, XwnEntryRecord[12], (ULONG_PTR)Caller);
    XwnPagingText(10, Text, 0xFFFFFFFF);
    RtlStringCbPrintfA(Text, sizeof(Text), "IDR: %08lx  Stall: %lu  CPU masks: %lx/%lx",
                      XwnEntryRecord[28], XwnEntryRecord[29], XwnEntryRecord[30], XwnEntryRecord[31]);
    XwnPagingText(12, Text, 0xFFFFFFFF);
    XwnPagingText(15, "Stopped BEFORE original HalInitSystem phase-0 body.", 0xFFFFFFFF);
    XwnPagingText(17, "Storage initialization and boot-driver entry NOT reached.", 0xFFFFFFFF);
#endif
    XwnPagingText(20, "Photograph this screen, then reboot to the dashboard.", 0xFFFFFFFF);
    for (;;) __halt();
}
