/*
 * PROJECT:     Xbox NT5 Boot Video
 * LICENSE:     GPL-2.0-or-later
 * PURPOSE:     Windows 2000 boot-video calling convention adapters
 */
#include "precomp.h"

BOOLEAN
NTAPI
XwnNt5VidInitialize(BOOLEAN SetMode)
{
    /* Keep the firmware scanout used by the Xbox framebuffer miniport.
     * Native NT5 does not provide a PC BIOS display-reset service here. */
    if (!VidInitialize(FALSE))
        return FALSE;
    if (SetMode)
        VidResetDisplay(FALSE);
    return TRUE;
}

VOID
NTAPI
XwnNt5VidResetDisplay(VOID)
{
    /* NT5 InbvResetDisplay passes no arguments. ReactOS takes a BOOLEAN;
     * exporting that routine directly corrupts NT5's return stack. */
    VidResetDisplay(FALSE);
}
