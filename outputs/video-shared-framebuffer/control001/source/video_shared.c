/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <ntddk.h>
#include <winerror.h>
#include "xwn_fb.h"
VOID NTAPI XwnVideoTrace(ULONG, ULONG, ULONG, ULONG);
static PVOID SharedOwner;
ULONG NTAPI XwnSharedMap(PVOID Device, ULONG Ram, ULONG Width, ULONG Height,
                         ULONG Stride, PVOID *Address)
{
    XWN_FB_VIEW View = {0};
    NTSTATUS Status;
    if (!Address || *Address) return ERROR_INVALID_PARAMETER;
    View.Size = sizeof(View); View.Version = XWN_FB_VERSION;
    View.Physical = Ram; View.Width = Width; View.Height = Height; View.Stride = Stride;
    Status = XwnFbAcquire(Device, &View);
    XwnVideoTrace(0x30, Status, View.Address, View.Physical);
    if (!NT_SUCCESS(Status)) return ERROR_INVALID_PARAMETER;
    SharedOwner = Device;
    *Address = (PVOID)(ULONG_PTR)View.Address;
    return ERROR_SUCCESS;
}
ULONG NTAPI XwnSharedUnmap(PVOID Device, PVOID Address)
{
    NTSTATUS Status = XwnFbRelease(Device, Address);
    XwnVideoTrace(0x31, Status, (ULONG_PTR)Address, (ULONG_PTR)Device);
    return NT_SUCCESS(Status) ? ERROR_SUCCESS : ERROR_INVALID_PARAMETER;
}
VOID NTAPI XwnSharedClose(VOID)
{
    if (SharedOwner)
    {
        NTSTATUS Status = XwnFbReleaseOwner(SharedOwner);
        XwnVideoTrace(0x32, Status, (ULONG_PTR)SharedOwner, 0);
        SharedOwner = NULL;
    }
}
