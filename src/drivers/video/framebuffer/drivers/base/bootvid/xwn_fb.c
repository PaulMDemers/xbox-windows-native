/* SPDX-License-Identifier: GPL-2.0-or-later
 * Permanent UC boot-video mapping, borrowed by one desktop adapter.
 * No map/unmap/cache transition or allocation occurs in these APIs. The boot
 * owner retains the mapping even at zero desktop references, including crash
 * and final shutdown. This is NOT an exclusive drawing or WC transition lock.
 */
#include <ntddk.h>
#include "xwn_fb.h"
NTSYSAPI BOOLEAN NTAPI InbvCheckDisplayOwnership(VOID);
static XWN_FB_VIEW Published;
static KSPIN_LOCK Lock;
static volatile LONG Ready;
static PVOID Owner;
static ULONG References;

BOOLEAN NTAPI XwnFbPublish(const XWN_FB_VIEW *View)
{
    /* Single boot initializer; publication precedes any desktop acquisition.
     * Reinitialization must not replace a pointer already lent to a consumer. */
    if (!View || Ready || View->Size != sizeof(*View) || View->Version != XWN_FB_VERSION ||
        !View->Address || (View->Address & 4095) || View->Address > MAXULONG - XWN_FB_BYTES ||
#ifdef XBOX_NT5_HD_RESERVATION
        View->Physical != XWN_HD_FB_PHYSICAL ||
#else
        (View->Physical != 0x03c00000 && View->Physical != 0x07c00000) ||
#endif
        View->ReservedBytes != XWN_FB_BYTES || View->CacheType != MmNonCached ||
        View->Width < 640 || View->Width > 1920 || View->Height < 480 || View->Height > 1080 ||
        View->Stride != View->Width * 4 || View->Height > XWN_FB_BYTES / View->Stride ||
        View->VisibleBytes != View->Height * View->Stride ||
        View->HiddenOffset < View->VisibleBytes || View->HiddenOffset >= XWN_FB_BYTES)
        return FALSE;
#ifdef XBOX_NT5_HD_RESERVATION
    if (!XwnHdLayoutValid(View->Physical, View->ReservedBytes, View->Width,
                          View->Height, View->Stride, View->HiddenOffset)) return FALSE;
#endif
    if (InterlockedCompareExchange(&Ready, -1, 0) != 0) return FALSE;
    KeInitializeSpinLock(&Lock);
    Published = *View;
    InterlockedExchange(&Ready, 1);
    return TRUE;
}

NTSTATUS NTAPI XwnFbAcquire(PVOID Device, PXWN_FB_VIEW View)
{
    KIRQL Irql;
    NTSTATUS Status = STATUS_INVALID_PARAMETER;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL || !Device || !View ||
        View->Size != sizeof(*View) || View->Version != XWN_FB_VERSION)
        return Status;
#ifdef XBOX_NT5_HD_RESERVATION
    if (View->ReservedBytes != XWN_FB_BYTES) return Status;
#endif
    if (InterlockedCompareExchange(&Ready, 1, 1) != 1) return STATUS_DEVICE_NOT_READY;
    /* A precondition, not proof of quiescence: no pointer is replaced/freed. */
    if (InbvCheckDisplayOwnership()) return STATUS_DEVICE_BUSY;
    KeAcquireSpinLock(&Lock, &Irql);
    if (View->Physical == Published.Physical && View->Width == Published.Width &&
        View->Height == Published.Height && View->Stride == Published.Stride &&
        !View->Address && (!References || Owner == Device) && References < XWN_FB_MAX_REFS)
    {
        Owner = Device;
        ++References;
        *View = Published;
        Status = STATUS_SUCCESS;
    }
    KeReleaseSpinLock(&Lock, Irql);
    return Status;
}

NTSTATUS NTAPI XwnFbRelease(PVOID Device, PVOID Address)
{
    KIRQL Irql;
    NTSTATUS Status = STATUS_INVALID_PARAMETER;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL || !Device || !Address ||
        InterlockedCompareExchange(&Ready, 1, 1) != 1) return Status;
    KeAcquireSpinLock(&Lock, &Irql);
    if (References && Owner == Device && (ULONG_PTR)Address == Published.Address)
    {
        if (!--References) Owner = NULL;
        Status = STATUS_SUCCESS;
    }
    KeReleaseSpinLock(&Lock, Irql);
    return Status;
}

NTSTATUS NTAPI XwnFbReleaseOwner(PVOID Device)
{
    KIRQL Irql;
    NTSTATUS Status = STATUS_INVALID_PARAMETER;
    if (KeGetCurrentIrql() != PASSIVE_LEVEL || !Device ||
        InterlockedCompareExchange(&Ready, 1, 1) != 1) return Status;
    KeAcquireSpinLock(&Lock, &Irql);
    if (!References || Owner == Device)
    {
        Owner = NULL;
        References = 0;
        Status = STATUS_SUCCESS;
    }
    KeReleaseSpinLock(&Lock, Irql);
    return Status;
}
