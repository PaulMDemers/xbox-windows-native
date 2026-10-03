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
    XwnPagingText(20, "Photograph this screen, then reboot to the dashboard.", 0xFFFFFFFF);
    for (;;) __halt();
}
