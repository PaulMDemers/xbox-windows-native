/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "vfat.h"

/* Count the FATX root's allocated chain before constructing its cache stream.
 * Brent cycle detection bounds corrupt chains without allocating a bitmap. */
NTSTATUS FatXRootSize839(PDEVICE_EXTENSION DeviceExt, PULONG Size)
{
    ULONG Current = 1, Next, Anchor = 1, Power = 1, Span = 0, Count = 0;
    ULONG Maximum = DeviceExt->FatInfo.NumberOfClusters + 1;
    ULONG ClusterBytes = DeviceExt->FatInfo.BytesPerCluster;
    NTSTATUS Status;
    *Size = 0;
    if (!Maximum || !ClusterBytes || !vfatVolumeIsFatX(DeviceExt))
        return STATUS_FILE_CORRUPT_ERROR;
    for (;;)
    {
        if (!Current || Current > Maximum || Count >= Maximum ||
            Count >= 0xffffffffUL / ClusterBytes)
            return STATUS_FILE_CORRUPT_ERROR;
        ++Count;
        Status = GetNextCluster(DeviceExt, Current, &Next);
        if (!NT_SUCCESS(Status))
            return Status;
        if (Next == 0xffffffff)
        {
            *Size = Count * ClusterBytes;
            return STATUS_SUCCESS;
        }
        if (!Next || Next > Maximum)
            return STATUS_FILE_CORRUPT_ERROR;
        ++Span;
        if (Next == Anchor)
            return STATUS_FILE_CORRUPT_ERROR;
        if (Span == Power)
        {
            Anchor = Next;
            Span = 0;
            if (Power <= Maximum / 2)
                Power *= 2;
        }
        Current = Next;
    }
}
