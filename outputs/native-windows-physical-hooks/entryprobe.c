/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

#ifdef XBOX_NT5_PHASE0_PREFLIGHT
typedef ULONG (NTAPI *XWN_PHASE_CALLBACK)(ULONG, PLOADER_PARAMETER_BLOCK, PVOID, PULONG);
static XWN_PHASE_CALLBACK XwnPhaseCallback;
static ULONG XwnPhaseStep;

VOID HalpXwnProcessorBoundary(BOOLEAN Complete, ULONG Processor,
                             PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    ULONG State[5];
    _disable();
    if (!XwnPhaseCallback || Processor != 0 || XwnPhaseStep != (Complete ? 1 : 0))
        for (;;) __halt();
    State[0] = Processor;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    if (XwnPhaseCallback(Complete ? 20 : 10, LoaderBlock, Caller, State) != 0x50524330)
        for (;;) __halt();
    XwnPhaseStep = Complete ? 2 : 1;
}

#ifndef XBOX_NT5_HALBASE_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID HalpXwnPhase0(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    ULONG State[5];
    _disable();
    if (!XwnPhaseCallback || XwnPhaseStep != 2 || Phase != 0) for (;;) __halt();
    State[0] = Phase;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    XwnPhaseStep = 3;
#ifdef XBOX_NT5_HALBASE_PREFLIGHT
    if (XwnPhaseCallback(30, LoaderBlock, Caller, State) == 0x50524330) return;
#else
    XwnPhaseCallback(30, LoaderBlock, Caller, State);
#endif
    for (;;) __halt();
}
#endif


#ifdef XBOX_NT5_ENTRY_PREFLIGHT
typedef VOID (NTAPI *XWN_CHECKPOINT)(ULONG, PLOADER_PARAMETER_BLOCK, PVOID);
static XWN_CHECKPOINT XwnCheckpoint;

DECLSPEC_NORETURN VOID
HalpXwnFirstProcessor(ULONG Processor, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    _disable();
    if (XwnCheckpoint) XwnCheckpoint(Processor, LoaderBlock, Caller);
    for (;;) __halt();
}
#endif

ULONG NTAPI XwnConfigureEntryProbe(PVOID Callback, ULONG Signature)
{
#if defined(XBOX_NT5_HOOKS_PREFLIGHT)
    if (Signature != 0x52474E54 || !Callback || XwnPhaseCallback) return 0;
    XwnPhaseCallback = (XWN_PHASE_CALLBACK)Callback;
    return 0x52474854;
#elif defined(XBOX_NT5_CLOCK_PREFLIGHT)
    if (Signature != 0x434C4E54 || !Callback || XwnPhaseCallback) return 0;
    XwnPhaseCallback = (XWN_PHASE_CALLBACK)Callback;
    return 0x434C4854;
#elif defined(XBOX_NT5_TIMER_PREFLIGHT)
    if (Signature != 0x54494E54 || !Callback || XwnPhaseCallback) return 0;
    XwnPhaseCallback = (XWN_PHASE_CALLBACK)Callback;
    return 0x54494854;
#elif defined(XBOX_NT5_HALBASE_PREFLIGHT)
    if (Signature != 0x42414E54 || !Callback || XwnPhaseCallback) return 0;
    XwnPhaseCallback = (XWN_PHASE_CALLBACK)Callback;
    return 0x42414854;
#elif defined(XBOX_NT5_PHASE0_PREFLIGHT)
    if (Signature != 0x50304E54 || !Callback || XwnPhaseCallback) return 0;
    XwnPhaseCallback = (XWN_PHASE_CALLBACK)Callback;
    return 0x50304854;
#elif defined(XBOX_NT5_ENTRY_PREFLIGHT)
    if (Signature != 0x58454E54 || !Callback || XwnCheckpoint) return 0;
    XwnCheckpoint = (XWN_CHECKPOINT)Callback;
    return 0x58484C54;
#else
    return 0; /* Ordinary HALs cannot arm this diagnostic. */
#endif
}

#ifdef XBOX_NT5_HALBASE_PREFLIGHT
extern LONG HalpEisaELCR;
extern UCHAR HalpCmosCenturyOffset;
#ifdef XBOX_NT5_TIMER_PREFLIGHT
static ULONG XwnRtcIdtBefore[3];
#else
DECLSPEC_NORETURN
#endif
VOID HalpXwnBaseReady(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock,
                                       PVOID Caller, NTSTATUS Status)
{
    ULONG State[14], Flags = __readeflags();
    _disable();
    if (!XwnPhaseCallback || XwnPhaseStep != 3 || Phase != 0) for (;;) __halt();
    State[0] = Phase;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    State[5] = KeGetCurrentPrcb()->MajorVersion;
    State[6] = KeGetCurrentPrcb()->BuildType;
    State[7] = HalpBuildType;
    State[8] = HalpEisaELCR;
    State[9] = __inbyte(0x21) | (__inbyte(0xa1) << 8);
    State[10] = HalpCmosCenturyOffset;
    State[11] = (HalQuerySystemInformation == HaliQuerySystemInformation) |
                ((HalSetSystemInformation == HaliSetSystemInformation) << 1) |
                ((HalInitPnpDriver == HaliInitPnpDriver) << 2) |
                ((HalGetDmaAdapter == HalpGetDmaAdapter) << 3) |
                ((HalGetInterruptTranslator == HalpNt5GetInterruptTranslator) << 4) |
                ((HalResetDisplay == HalpBiosDisplayReset) << 5) |
                ((HalHaltSystem == HaliHaltSystem) << 6);
    State[12] = Flags;
    State[13] = Status;
    XwnPhaseStep = 4;
#ifdef XBOX_NT5_TIMER_PREFLIGHT
    {
        KDESCRIPTOR Idt;
        PULONG Entry;
        __sidt(&Idt.Limit);
        Entry = (PULONG)(Idt.Base + 0x38 * 8);
        XwnRtcIdtBefore[0] = Entry[0];
        XwnRtcIdtBefore[1] = Entry[1];
        XwnRtcIdtBefore[2] = Idt.Base;
        if (XwnPhaseCallback(40, LoaderBlock, Caller, State) == 0x50524330)
        {
            __writeeflags(Flags);
            return;
        }
    }
#else
    XwnPhaseCallback(40, LoaderBlock, Caller, State);
#endif
    for (;;) __halt();
}
#endif

#ifdef XBOX_NT5_TIMER_PREFLIGHT
#ifndef XBOX_NT5_CLOCK_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID HalpXwnTimerReady(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    ULONG State[14], Flags = __readeflags();
    KDESCRIPTOR Idt;
    PULONG Entry;
    _disable();
    if (!XwnPhaseCallback || XwnPhaseStep != 4 || Phase != 0) for (;;) __halt();
    __sidt(&Idt.Limit);
    Entry = (PULONG)(Idt.Base + 0x38 * 8);
    State[0] = Phase;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    State[5] = XwnRtcIdtBefore[0];
    State[6] = XwnRtcIdtBefore[1];
    State[7] = XwnRtcIdtBefore[2];
    State[8] = Entry[0];
    State[9] = Entry[1];
    State[10] = Idt.Base;
    State[11] = __inbyte(0x21) | (__inbyte(0xa1) << 8);
    State[12] = Flags;
    State[13] = 0;
    XwnPhaseStep = 5;
#ifdef XBOX_NT5_CLOCK_PREFLIGHT
    if (XwnPhaseCallback(50, LoaderBlock, Caller, State) == 0x50524330)
    {
        __writeeflags(Flags);
        return;
    }
#else
    XwnPhaseCallback(50, LoaderBlock, Caller, State);
#endif
    for (;;) __halt();
}
#endif

#ifdef XBOX_NT5_CLOCK_PREFLIGHT
extern ULONG HalpCurrentRollOver, HalpCurrentTimeIncrement, HalpLargestClockMS;
extern HALP_ROLLOVER HalpRolloverTable[15];
extern BOOLEAN HalpProfilingStopped;
#ifndef XBOX_NT5_HOOKS_PREFLIGHT
DECLSPEC_NORETURN
#endif
VOID HalpXwnClockReady(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    ULONG State[16], Flags = __readeflags(), Counter;
    _disable();
    if (!XwnPhaseCallback || XwnPhaseStep != 5 || Phase != 0) for (;;) __halt();
    State[0] = Phase;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    State[5] = HalpCurrentRollOver;
    State[6] = HalpCurrentTimeIncrement;
    State[7] = HalpLargestClockMS;
    State[8] = HalpRolloverTable[14].RollOver;
    State[9] = HalpRolloverTable[14].Increment;
    State[10] = HalpProfilingStopped;
    State[11] = __inbyte(0x21) | (__inbyte(0xa1) << 8);
    State[12] = Flags;
    HalpAcquireCmosSpinLock();
    State[13] = HalpReadCmos(0x0b);
    HalpReleaseCmosSpinLock();
    /* Same channel-0 latch sequence as HalpRead8254Value; no reprogramming. */
    __outbyte(0x43, 0);
    __nop();
    Counter = __inbyte(0x40);
    __nop();
    Counter |= __inbyte(0x40) << 8;
    State[14] = Counter;
    State[15] = HalpRolloverTable[0].Increment;
    XwnPhaseStep = 6;
#ifdef XBOX_NT5_HOOKS_PREFLIGHT
    if (XwnPhaseCallback(60, LoaderBlock, Caller, State) == 0x50524330)
    {
        __writeeflags(Flags);
        return;
    }
#else
    XwnPhaseCallback(60, LoaderBlock, Caller, State);
#endif
    for (;;) __halt();
}
#endif

#ifdef XBOX_NT5_HOOKS_PREFLIGHT
ULONG HalpXwnPartitionHookMask(VOID);
ULONG HalpXwnSavedPartitionMask(VOID);
DECLSPEC_NORETURN VOID HalpXwnHooksReady(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
{
    ULONG State[9], Flags = __readeflags();
    _disable();
    if (!XwnPhaseCallback || XwnPhaseStep != 6 || Phase != 0) for (;;) __halt();
    State[0] = Phase;
    State[1] = KeGetPcr()->IDR;
    State[2] = KeGetPcr()->StallScaleFactor;
    State[3] = (ULONG)HalpActiveProcessors;
    State[4] = (ULONG)HalpDefaultInterruptAffinity;
    State[5] = HalpXwnPartitionHookMask();
    State[6] = HalpXwnSavedPartitionMask();
    State[7] = __inbyte(0x21) | (__inbyte(0xa1) << 8);
    State[8] = Flags;
    XwnPhaseStep = 7;
    XwnPhaseCallback(70, LoaderBlock, Caller, State);
    for (;;) __halt();
}
#endif
