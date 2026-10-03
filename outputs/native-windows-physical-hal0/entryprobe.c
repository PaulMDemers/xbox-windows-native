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

DECLSPEC_NORETURN VOID HalpXwnPhase0(ULONG Phase, PLOADER_PARAMETER_BLOCK LoaderBlock, PVOID Caller)
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
    XwnPhaseCallback(30, LoaderBlock, Caller, State);
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
#if defined(XBOX_NT5_PHASE0_PREFLIGHT)
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
