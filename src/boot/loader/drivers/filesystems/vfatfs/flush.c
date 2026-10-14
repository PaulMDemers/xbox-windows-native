/*
 * PROJECT:     VFAT Filesystem
 * LICENSE:     GPL-2.0-or-later (https://spdx.org/licenses/GPL-2.0-or-later)
 * PURPOSE:     Flushing routines
 * COPYRIGHT:   Copyright 2004-2013 Eric Kohl <eric.kohl@reactos.org>
 *              Copyright 2014-2018 Pierre Schweitzer <pierre@reactos.org>
 */

/* INCLUDES *****************************************************************/

#include "vfat.h"

#define NDEBUG
#include <debug.h>

/* FUNCTIONS ****************************************************************/

static
NTSTATUS
VfatFlushFile(
    PDEVICE_EXTENSION DeviceExt,
    PVFATFCB Fcb)
{
    IO_STATUS_BLOCK IoStatus;
    NTSTATUS Status;

    DPRINT("VfatFlushFile(DeviceExt %p, Fcb %p) for '%wZ'\n", DeviceExt, Fcb, &Fcb->PathNameU);

    CcFlushCache(&Fcb->SectionObjectPointers, NULL, 0, &IoStatus);
    if (IoStatus.Status == STATUS_INVALID_PARAMETER)
    {
        /* FIXME: Caching was possible not initialized */
        IoStatus.Status = STATUS_SUCCESS;
    }

    ExAcquireResourceExclusiveLite(&DeviceExt->DirResource, TRUE);
    if (BooleanFlagOn(Fcb->Flags, FCB_IS_DIRTY))
    {
        Status = VfatUpdateEntry(DeviceExt, Fcb);
        if (!NT_SUCCESS(Status))
        {
            IoStatus.Status = Status;
        }
    }
    ExReleaseResourceLite(&DeviceExt->DirResource);

    return IoStatus.Status;
}

/* The caller holds DirResource once. Pin a stable set of FCBs before
 * dropping it: ordinary file writes/flushes acquire MainResource first and
 * may then need DirResource. Waiting for MainResource with DirResource held
 * would deadlock those operations. Restore the caller's lock on every exit. */
static
NTSTATUS
VfatFlushPinnedFiles(PDEVICE_EXTENSION DeviceExt)
{
    PLIST_ENTRY Entry;
    PVFATFCB Fcb, *Files;
    ULONG Count = 0, Index, Pass;
    NTSTATUS Status, Result = STATUS_SUCCESS;

    ASSERT(ExIsResourceAcquiredExclusive(&DeviceExt->DirResource));
    for (Entry = DeviceExt->FcbListHead.Flink;
         Entry != &DeviceExt->FcbListHead; Entry = Entry->Flink)
    {
        Fcb = CONTAINING_RECORD(Entry, VFATFCB, FcbListEntry);
        if (!BooleanFlagOn(Fcb->Flags, FCB_IS_FAT | FCB_IS_VOLUME))
        {
            if (Count == MAXULONG / sizeof(*Files))
                return STATUS_INSUFFICIENT_RESOURCES;
            ++Count;
        }
    }
    if (!Count)
        return STATUS_SUCCESS;
    Files = ExAllocatePoolWithTag(NonPagedPool, Count * sizeof(*Files), 'lFfV');
    if (!Files)
        return STATUS_INSUFFICIENT_RESOURCES;
    Index = 0;
    for (Entry = DeviceExt->FcbListHead.Flink;
         Entry != &DeviceExt->FcbListHead; Entry = Entry->Flink)
    {
        Fcb = CONTAINING_RECORD(Entry, VFATFCB, FcbListEntry);
        if (!BooleanFlagOn(Fcb->Flags, FCB_IS_FAT | FCB_IS_VOLUME))
        {
            vfatGrabFCB(DeviceExt, Fcb);
            Files[Index++] = Fcb;
        }
    }
    ASSERT(Index == Count);
    ExReleaseResourceLite(&DeviceExt->DirResource);
    /* Flush files before directories, as in the serialized volume path. */
    for (Pass = 0; Pass < 2; ++Pass)
    {
        for (Index = 0; Index < Count; ++Index)
        {
            Fcb = Files[Index];
            if (!!vfatFCBIsDirectory(Fcb) != !!Pass)
                continue;
            ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
            Status = VfatFlushFile(DeviceExt, Fcb);
            ExReleaseResourceLite(&Fcb->MainResource);
            if (!NT_SUCCESS(Status))
                Result = Status;
        }
    }
    ExAcquireResourceExclusiveLite(&DeviceExt->DirResource, TRUE);
    for (Index = 0; Index < Count; ++Index)
        vfatReleaseFCB(DeviceExt, Files[Index]);
    ExFreePoolWithTag(Files, 'lFfV');
    return Result;
}

NTSTATUS
VfatFlushVolume(
    PDEVICE_EXTENSION DeviceExt,
    PVFATFCB VolumeFcb,
    BOOLEAN ConcurrentFiles)
{
    PLIST_ENTRY ListEntry;
    PVFATFCB Fcb;
    NTSTATUS Status, ReturnStatus = STATUS_SUCCESS;
    PIRP Irp;
    KEVENT Event;
    IO_STATUS_BLOCK IoStatusBlock;

    DPRINT("VfatFlushVolume(DeviceExt %p, VolumeFcb %p)\n", DeviceExt, VolumeFcb);

    ASSERT(VolumeFcb == DeviceExt->VolumeFcb);

    if (ConcurrentFiles)
    {
        ReturnStatus = VfatFlushPinnedFiles(DeviceExt);
    }
    else
    {
        /* Lock/dismount callers retain their namespace exclusion throughout. */
        ListEntry = DeviceExt->FcbListHead.Flink;
        while (ListEntry != &DeviceExt->FcbListHead)
        {
            Fcb = CONTAINING_RECORD(ListEntry, VFATFCB, FcbListEntry);
            ListEntry = ListEntry->Flink;
            if (!vfatFCBIsDirectory(Fcb))
            {
                ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
                Status = VfatFlushFile(DeviceExt, Fcb);
                ExReleaseResourceLite (&Fcb->MainResource);
                if (!NT_SUCCESS(Status))
                {
                    DPRINT1("VfatFlushFile failed, status = %x\n", Status);
                    ReturnStatus = Status;
                }
            }
            /* FIXME: Stop flushing if this is a removable media and the media was removed */
        }

        ListEntry = DeviceExt->FcbListHead.Flink;
        while (ListEntry != &DeviceExt->FcbListHead)
        {
            Fcb = CONTAINING_RECORD(ListEntry, VFATFCB, FcbListEntry);
            ListEntry = ListEntry->Flink;
            if (vfatFCBIsDirectory(Fcb))
            {
                ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
                Status = VfatFlushFile(DeviceExt, Fcb);
                ExReleaseResourceLite (&Fcb->MainResource);
                if (!NT_SUCCESS(Status))
                {
                    DPRINT1("VfatFlushFile failed, status = %x\n", Status);
                    ReturnStatus = Status;
                }
            }
            /* FIXME: Stop flushing if this is a removable media and the media was removed */
        }

    }

    Fcb = (PVFATFCB) DeviceExt->FATFileObject->FsContext;

    ExAcquireResourceExclusiveLite(&DeviceExt->FatResource, TRUE);
    Status = VfatFlushFile(DeviceExt, Fcb);
    ExReleaseResourceLite(&DeviceExt->FatResource);

    /* Prepare an IRP to flush device buffers */
    Irp = IoBuildSynchronousFsdRequest(IRP_MJ_FLUSH_BUFFERS,
                                       DeviceExt->StorageDevice,
                                       NULL, 0, NULL, &Event,
                                       &IoStatusBlock);
    if (Irp != NULL)
    {
        KeInitializeEvent(&Event, NotificationEvent, FALSE);

        Status = IoCallDriver(DeviceExt->StorageDevice, Irp);
        if (Status == STATUS_PENDING)
        {
            KeWaitForSingleObject(&Event, Executive, KernelMode, FALSE, NULL);
            Status = IoStatusBlock.Status;
        }

        /* Ignore device not supporting flush operation */
        if (Status == STATUS_INVALID_DEVICE_REQUEST)
        {
            DPRINT1("Flush not supported, ignored\n");
            Status = STATUS_SUCCESS;

        }
    }
    else
    {
        Status = STATUS_INSUFFICIENT_RESOURCES;
    }

    if (!NT_SUCCESS(Status))
    {
        DPRINT1("VfatFlushFile failed, status = %x\n", Status);
        ReturnStatus = Status;
    }

    return ReturnStatus;
}

NTSTATUS
VfatFlush(
    PVFAT_IRP_CONTEXT IrpContext)
{
    NTSTATUS Status;
    PVFATFCB Fcb;

    /* This request is not allowed on the main device object. */
    if (IrpContext->DeviceObject == VfatGlobalData->DeviceObject)
    {
        IrpContext->Irp->IoStatus.Information = 0;
        return STATUS_INVALID_DEVICE_REQUEST;
    }

    Fcb = (PVFATFCB)IrpContext->FileObject->FsContext;
    ASSERT(Fcb);

    if (BooleanFlagOn(Fcb->Flags, FCB_IS_VOLUME))
    {
        ExAcquireResourceExclusiveLite(&IrpContext->DeviceExt->DirResource, TRUE);
        Status = VfatFlushVolume(IrpContext->DeviceExt, Fcb, TRUE);
        ExReleaseResourceLite(&IrpContext->DeviceExt->DirResource);
    }
    else
    {
        ExAcquireResourceExclusiveLite(&Fcb->MainResource, TRUE);
        Status = VfatFlushFile(IrpContext->DeviceExt, Fcb);
        ExReleaseResourceLite (&Fcb->MainResource);
    }

    IrpContext->Irp->IoStatus.Information = 0;
    return Status;
}

/* EOF */
