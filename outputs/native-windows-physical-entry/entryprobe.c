/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <hal.h>

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
#ifdef XBOX_NT5_ENTRY_PREFLIGHT
    if (Signature != 0x58454E54 || !Callback || XwnCheckpoint) return 0;
    XwnCheckpoint = (XWN_CHECKPOINT)Callback;
    return 0x58484C54;
#else
    return 0; /* Ordinary HALs cannot arm this diagnostic. */
#endif
}
