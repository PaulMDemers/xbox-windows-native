/*
 * PROJECT:         Xbox HAL
 * LICENSE:         GPL-2.0-or-later (https://spdx.org/licenses/GPL-2.0-or-later)
 * PURPOSE:         Xbox specific handling of partition tables
 * COPYRIGHT:       Copyright 2004 Ge van Geldorp (gvg@reactos.com)
 *                  Copyright 2020 Stanislav Motylkov (x86corez@gmail.com)
 */

/* INCLUDES *****************************************************************/

#include "halxbox.h"
#include <internal/tag.h>
#include <xboxpart.h>

#define NDEBUG
#include <debug.h>

#define XBOX_SIGNATURE_SECTOR 3
#define XBOX_SIGNATURE        ('B' | ('R' << 8) | ('F' << 16) | ('R' << 24))
#define PARTITION_SIGNATURE   0xaa55

/* VARIABLES ***************************************************************/

static pHalExamineMBR NtoskrnlExamineMBR;
static pHalIoReadPartitionTable NtoskrnlIoReadPartitionTable;
static pHalIoSetPartitionInformation NtoskrnlIoSetPartitionInformation;
static pHalIoWritePartitionTable NtoskrnlIoWritePartitionTable;

static struct
{
    ULONG SectorStart;
    ULONG SectorCount;
    CHAR PartitionType;
} XboxPartitions[] =
{
    /* This is in the \Device\Harddisk0\Partition.. order used by the Xbox kernel */
    { 0x0055F400, 0x0098f800, PARTITION_FAT32  }, /* Store, E: */
    { 0x00465400, 0x000FA000, PARTITION_FAT_16 }, /* System, C: */
    { 0x00000400, 0x00177000, PARTITION_FAT_16 }, /* Cache1, X: */
    { 0x00177400, 0x00177000, PARTITION_FAT_16 }, /* Cache2, Y: */
    { 0x002EE400, 0x00177000, PARTITION_FAT_16 }  /* Cache3, Z: */
};

#define XBOX_PARTITION_COUNT (sizeof(XboxPartitions) / sizeof(XboxPartitions[0]))

/* FUNCTIONS ***************************************************************/


static NTSTATUS
HalpXboxReadSector(IN PDEVICE_OBJECT DeviceObject,
                   IN ULONG SectorSize,
                   IN PLARGE_INTEGER SectorOffset,
                   OUT PVOID Sector)
{
    IO_STATUS_BLOCK StatusBlock;
    KEVENT Event;
    PIRP Irp;
    NTSTATUS Status;

    DPRINT("HalpXboxReadSector(%p %lu 0x%08x%08x %p)\n",
           DeviceObject, SectorSize, SectorOffset->u.HighPart, SectorOffset->u.LowPart, Sector);

    ASSERT(DeviceObject);
    ASSERT(Sector);

    KeInitializeEvent(&Event,
                      NotificationEvent,
                      FALSE);

    /* Read the sector */
    Irp = IoBuildSynchronousFsdRequest(IRP_MJ_READ,
                                       DeviceObject,
                                       Sector,
                                       SectorSize,
                                       SectorOffset,
                                       &Event,
                                       &StatusBlock);
    if (!Irp) return STATUS_INSUFFICIENT_RESOURCES;

    Status = IoCallDriver(DeviceObject,
                          Irp);
    if (Status == STATUS_PENDING)
    {
        KeWaitForSingleObject(&Event,
                              Executive,
                              KernelMode,
                              FALSE,
                              NULL);
        Status = StatusBlock.Status;
    }

    if (!NT_SUCCESS(Status))
    {
        DPRINT("Reading sector failed (Status 0x%08lx)\n", Status);
        return Status;
    }

    return Status;
}

static NTSTATUS FASTCALL
HalpXboxDeviceHasXboxPartitioning(IN PDEVICE_OBJECT DeviceObject,
                                  IN ULONG SectorSize,
                                  OUT BOOLEAN *HasXboxPartitioning)
{
    PVOID SectorData;
    LARGE_INTEGER Offset;
    NTSTATUS Status;
    BOOLEAN HasMBRPartitioning;

    DPRINT("HalpXboxDeviceHasXboxPartitioning(%p %lu %p)\n",
           DeviceObject,
           SectorSize,
           HasXboxPartitioning);

    SectorData = ExAllocatePoolWithTag(PagedPool, SectorSize, TAG_HAL_XBOX);
    if (!SectorData)
    {
        return STATUS_NO_MEMORY;
    }

    Offset.QuadPart = 0;
    Status = HalpXboxReadSector(DeviceObject, SectorSize, &Offset, SectorData);
    if (!NT_SUCCESS(Status))
    {
        goto Cleanup;
    }

    HasMBRPartitioning = (*((USHORT *)SectorData + (SectorSize / sizeof(USHORT)) - 1) == PARTITION_SIGNATURE);
    if (HasMBRPartitioning)
    {
        *HasXboxPartitioning = FALSE;
        goto Cleanup;
    }

    Offset.QuadPart = XBOX_SIGNATURE_SECTOR * SectorSize;
    Status = HalpXboxReadSector(DeviceObject, SectorSize, &Offset, SectorData);
    if (!NT_SUCCESS(Status))
    {
        goto Cleanup;
    }

    DPRINT("Signature 0x%02x 0x%02x 0x%02x 0x%02x\n",
           *((UCHAR *) SectorData), *((UCHAR *) SectorData + 1), *((UCHAR *) SectorData + 2), *((UCHAR *) SectorData + 3));
    *HasXboxPartitioning = (XBOX_SIGNATURE == *((ULONG *) SectorData));
Cleanup:
    ExFreePoolWithTag(SectorData, TAG_HAL_XBOX);
    if (NT_SUCCESS(Status))
    {
        DPRINT("%s partitioning found\n", *HasXboxPartitioning ? "Xbox" : "MBR");
    }

    return Status;
}

static VOID FASTCALL
HalpXboxExamineMBR(IN PDEVICE_OBJECT DeviceObject,
                   IN ULONG SectorSize,
                   IN ULONG MBRTypeIdentifier,
                   OUT PVOID *Buffer)
{
    BOOLEAN HasXboxPartitioning;
    NTSTATUS Status;

    DPRINT("HalpXboxExamineMBR(%p %lu %lx %p)\n",
           DeviceObject,
           SectorSize,
           MBRTypeIdentifier,
           Buffer);

    *Buffer = NULL;

    Status = HalpXboxDeviceHasXboxPartitioning(DeviceObject, SectorSize, &HasXboxPartitioning);
    if (!NT_SUCCESS(Status))
    {
        return;
    }

    if (!HasXboxPartitioning)
    {
        DPRINT("Delegating to standard MBR code\n");
        NtoskrnlExamineMBR(DeviceObject, SectorSize, MBRTypeIdentifier, Buffer);
        return;
    }

    /* Buffer already set to NULL */
    return;
}

/* Read-only debugger telemetry: magic, calls, stage, status, table status,
 * count, device length low/high, returned bytes, sector size, BRFR status. */
volatile ULONG XwnExtendedPartitionTrace[16] = {0x58575054};

/* Require an exact device length before trusting extended on-disk extents.
 * Unsupported length queries fail closed; CHS rounding is not a substitute.
 */
static NTSTATUS
HalpXboxReadExtendedLayout(PDEVICE_OBJECT Device, ULONG SectorSize,
                          XWN_XBOX_PARTITION *Parts, unsigned int *Count,
                          int *TableStatus)
{
    PVOID Buffer;
    LARGE_INTEGER Offset;
    GET_LENGTH_INFORMATION Length;
    IO_STATUS_BLOCK Io;
    KEVENT Event;
    PIRP Irp;
    NTSTATUS Status;
    XwnExtendedPartitionTrace[2] = 30;
    *TableStatus = XWN_XBOX_TABLE_INVALID;
    if (SectorSize != 512) return STATUS_NOT_SUPPORTED;
    Buffer = ExAllocatePoolWithTag(PagedPool, SectorSize, TAG_HAL_XBOX);
    if (!Buffer) return STATUS_INSUFFICIENT_RESOURCES;
    Offset.QuadPart = 0;
    Status = HalpXboxReadSector(Device, SectorSize, &Offset, Buffer);
    XwnExtendedPartitionTrace[3] = Status;
    if (!NT_SUCCESS(Status)) goto Done;
    XwnExtendedPartitionTrace[2] = 35;
    /* The first parse only detects absence. An unknown capacity cannot validate. */
    *TableStatus = XwnXboxParsePartitionTable(Buffer, SectorSize, 0, Parts, Count);
    XwnExtendedPartitionTrace[4] = *TableStatus;
    if (*TableStatus == XWN_XBOX_TABLE_ABSENT) goto Done;
    RtlZeroMemory(&Io, sizeof(Io));
    RtlZeroMemory(&Length, sizeof(Length));
    KeInitializeEvent(&Event, NotificationEvent, FALSE);
    Irp = IoBuildDeviceIoControlRequest(IOCTL_DISK_GET_LENGTH_INFO, Device,
            NULL, 0, &Length, sizeof(Length), FALSE, &Event, &Io);
    if (!Irp) { Status = STATUS_INSUFFICIENT_RESOURCES; goto Done; }
    Status = IoCallDriver(Device, Irp);
    if (Status == STATUS_PENDING)
    {
        KeWaitForSingleObject(&Event, Executive, KernelMode, FALSE, NULL);
        Status = Io.Status;
    }
    /* Windows 2000 may return STATUS_NOT_IMPLEMENTED for GET_LENGTH_INFO.
     * Query Partition0's native length, never a CHS estimate or table end. */
    if (Status == STATUS_NOT_IMPLEMENTED || Status == STATUS_INVALID_DEVICE_REQUEST ||
        Status == STATUS_NOT_SUPPORTED)
    {
        PARTITION_INFORMATION WholeDisk;
        XwnExtendedPartitionTrace[11] = 1;
        RtlZeroMemory(&WholeDisk, sizeof(WholeDisk));
        RtlZeroMemory(&Io, sizeof(Io));
        KeInitializeEvent(&Event, NotificationEvent, FALSE);
        Irp = IoBuildDeviceIoControlRequest(IOCTL_DISK_GET_PARTITION_INFO, Device,
                NULL, 0, &WholeDisk, sizeof(WholeDisk), FALSE, &Event, &Io);
        if (!Irp) { Status = STATUS_INSUFFICIENT_RESOURCES; goto Done; }
        Status = IoCallDriver(Device, Irp);
        if (Status == STATUS_PENDING)
        {
            KeWaitForSingleObject(&Event, Executive, KernelMode, FALSE, NULL);
            Status = Io.Status;
        }
        XwnExtendedPartitionTrace[12] = Status;
        XwnExtendedPartitionTrace[13] = WholeDisk.StartingOffset.LowPart;
        XwnExtendedPartitionTrace[14] = WholeDisk.PartitionLength.LowPart;
        XwnExtendedPartitionTrace[15] = WholeDisk.PartitionLength.HighPart;
        if (!NT_SUCCESS(Status)) goto Done;
        if (Io.Information < sizeof(WholeDisk) || WholeDisk.PartitionNumber != 0 ||
            WholeDisk.StartingOffset.QuadPart != 0)
        { Status = STATUS_DISK_CORRUPT_ERROR; goto Done; }
        Length.Length = WholeDisk.PartitionLength;
        Io.Information = sizeof(Length);
    }
    XwnExtendedPartitionTrace[2] = 40;
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[6] = Length.Length.LowPart;
    XwnExtendedPartitionTrace[7] = Length.Length.HighPart;
    XwnExtendedPartitionTrace[8] = Io.Information;
    if (!NT_SUCCESS(Status)) goto Done;
    if (Io.Information < sizeof(Length) || Length.Length.QuadPart <= 0 ||
        (Length.Length.QuadPart & 511))
    { Status = STATUS_DISK_CORRUPT_ERROR; goto Done; }
    *TableStatus = XwnXboxParsePartitionTable(Buffer, SectorSize,
                         (ULONGLONG)Length.Length.QuadPart / 512, Parts, Count);
    if (*TableStatus != XWN_XBOX_TABLE_VALID) Status = STATUS_DISK_CORRUPT_ERROR;
Done:
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[4] = *TableStatus;
    XwnExtendedPartitionTrace[5] = *Count;
    ExFreePoolWithTag(Buffer, TAG_HAL_XBOX);
    return Status;
}

static NTSTATUS FASTCALL
HalpXboxIoReadPartitionTable(IN PDEVICE_OBJECT DeviceObject,
                             IN ULONG SectorSize,
                             IN BOOLEAN ReturnRecognizedPartitions,
                             OUT PDRIVE_LAYOUT_INFORMATION *PartitionBuffer)
{
    BOOLEAN HasXboxPartitioning;
    NTSTATUS Status;
    ULONG Part;
    PPARTITION_INFORMATION PartInfo;
    XWN_XBOX_PARTITION Parts[XWN_XBOX_MAX_PARTITIONS];
    unsigned int PartCount = XBOX_PARTITION_COUNT;
    int TableStatus;

    DPRINT("HalpXboxIoReadPartitionTable(%p %lu %x %p)\n",
           DeviceObject,
           SectorSize,
           ReturnRecognizedPartitions,
           PartitionBuffer);

    XwnExtendedPartitionTrace[1]++;
    XwnExtendedPartitionTrace[2] = 10;
    XwnExtendedPartitionTrace[9] = SectorSize;
    Status = HalpXboxDeviceHasXboxPartitioning(DeviceObject, SectorSize, &HasXboxPartitioning);
    XwnExtendedPartitionTrace[3] = Status;
    XwnExtendedPartitionTrace[10] = NT_SUCCESS(Status) ? HasXboxPartitioning : 0;
    if (!NT_SUCCESS(Status))
    {
        return Status;
    }

    if (!HasXboxPartitioning)
    {
        DPRINT("Delegating to standard MBR code\n");
        return NtoskrnlIoReadPartitionTable(DeviceObject, SectorSize,
                                            ReturnRecognizedPartitions, PartitionBuffer);
    }

    Status = HalpXboxReadExtendedLayout(DeviceObject, SectorSize, Parts,
                                        &PartCount, &TableStatus);
    if (!NT_SUCCESS(Status)) return Status;
    if (TableStatus == XWN_XBOX_TABLE_ABSENT) PartCount = XBOX_PARTITION_COUNT;

    *PartitionBuffer = (PDRIVE_LAYOUT_INFORMATION)ExAllocatePoolWithTag(
                        PagedPool,
                        sizeof(DRIVE_LAYOUT_INFORMATION) +
                        PartCount * sizeof(PARTITION_INFORMATION),
                        TAG_FILE_SYSTEM);
    if (*PartitionBuffer == NULL)
    {
        return STATUS_NO_MEMORY;
    }
    XwnExtendedPartitionTrace[2] = 90;
    (*PartitionBuffer)->PartitionCount = PartCount;
    (*PartitionBuffer)->Signature = PARTITION_SIGNATURE;
    for (Part = 0; Part < PartCount; Part++)
    {
        PartInfo = (*PartitionBuffer)->PartitionEntry + Part;
        PartInfo->StartingOffset.QuadPart = (ULONGLONG) (TableStatus == XWN_XBOX_TABLE_VALID ? Parts[Part].Start : XboxPartitions[Part].SectorStart) *
                                            (ULONGLONG) SectorSize;
        PartInfo->PartitionLength.QuadPart = (ULONGLONG) (TableStatus == XWN_XBOX_TABLE_VALID ? Parts[Part].Count : XboxPartitions[Part].SectorCount) *
                                             (ULONGLONG) SectorSize;
        PartInfo->HiddenSectors = 0;
        PartInfo->PartitionNumber = Part + 1;
        PartInfo->PartitionType = TableStatus == XWN_XBOX_TABLE_VALID ? PARTITION_FAT32 : XboxPartitions[Part].PartitionType;
        PartInfo->BootIndicator = FALSE;
        PartInfo->RecognizedPartition = TRUE;
        PartInfo->RewritePartition = FALSE;
        DPRINT(" %ld: nr: %d boot: %1x type: %x start: 0x%I64x count: 0x%I64x rec: %d\n",
               Part,
               PartInfo->PartitionNumber,
               PartInfo->BootIndicator,
               PartInfo->PartitionType,
               PartInfo->StartingOffset.QuadPart,
               PartInfo->PartitionLength.QuadPart,
               PartInfo->RecognizedPartition);
    }

    return STATUS_SUCCESS;
}

static NTSTATUS FASTCALL
HalpXboxIoSetPartitionInformation(IN PDEVICE_OBJECT DeviceObject,
                                  IN ULONG SectorSize,
                                  IN ULONG PartitionNumber,
                                  IN ULONG PartitionType)
{
    BOOLEAN HasXboxPartitioning;
    NTSTATUS Status;

    DPRINT("HalpXboxIoSetPartitionInformation(%p %lu %lu %lu)\n",
           DeviceObject,
           SectorSize,
           PartitionNumber,
           PartitionType);

    Status = HalpXboxDeviceHasXboxPartitioning(DeviceObject, SectorSize, &HasXboxPartitioning);
    if (!NT_SUCCESS(Status))
    {
        return Status;
    }

    if (!HasXboxPartitioning)
    {
        DPRINT("Delegating to standard MBR code\n");
        return NtoskrnlIoSetPartitionInformation(DeviceObject, SectorSize,
                                                 PartitionNumber, PartitionType);
    }

    /* Can't change the partitioning */
    DPRINT1("Xbox partitions are fixed, can't change them\n");
    return STATUS_ACCESS_DENIED;
}

static NTSTATUS FASTCALL
HalpXboxIoWritePartitionTable(IN PDEVICE_OBJECT DeviceObject,
                              IN ULONG SectorSize,
                              IN ULONG SectorsPerTrack,
                              IN ULONG NumberOfHeads,
                              IN PDRIVE_LAYOUT_INFORMATION PartitionBuffer)
{
    BOOLEAN HasXboxPartitioning;
    NTSTATUS Status;

    DPRINT("HalpXboxIoWritePartitionTable(%p %lu %lu %lu %p)\n",
           DeviceObject,
           SectorSize,
           SectorsPerTrack,
           NumberOfHeads,
           PartitionBuffer);

    Status = HalpXboxDeviceHasXboxPartitioning(DeviceObject, SectorSize, &HasXboxPartitioning);
    if (!NT_SUCCESS(Status))
    {
        return Status;
    }

    if (!HasXboxPartitioning)
    {
        DPRINT("Delegating to standard MBR code\n");
        return NtoskrnlIoWritePartitionTable(DeviceObject, SectorSize,
                                             SectorsPerTrack, NumberOfHeads,
                                             PartitionBuffer);
    }

    /* Can't change the partitioning */
    DPRINT1("Xbox partitions are fixed, can't change them\n");
    return STATUS_ACCESS_DENIED;
}

#define HalExamineMBR                   HALDISPATCH->HalExamineMBR
#define HalIoReadPartitionTable         HALDISPATCH->HalIoReadPartitionTable
#define HalIoSetPartitionInformation    HALDISPATCH->HalIoSetPartitionInformation
#define HalIoWritePartitionTable        HALDISPATCH->HalIoWritePartitionTable

void
HalpXboxInitPartIo(void)
{
    NtoskrnlExamineMBR = HalExamineMBR;
    HalExamineMBR = HalpXboxExamineMBR;
    NtoskrnlIoReadPartitionTable = HalIoReadPartitionTable;
    HalIoReadPartitionTable = HalpXboxIoReadPartitionTable;
    NtoskrnlIoSetPartitionInformation = HalIoSetPartitionInformation;
    HalIoSetPartitionInformation = HalpXboxIoSetPartitionInformation;
    NtoskrnlIoWritePartitionTable = HalIoWritePartitionTable;
    HalIoWritePartitionTable = HalpXboxIoWritePartitionTable;
}

/* EOF */

#ifdef XBOX_NT5_HOOKS_PREFLIGHT
ULONG HalpXwnPartitionHookMask(VOID)
{
    return (HalExamineMBR == HalpXboxExamineMBR) |
           ((HalIoReadPartitionTable == HalpXboxIoReadPartitionTable) << 1) |
           ((HalIoSetPartitionInformation == HalpXboxIoSetPartitionInformation) << 2) |
           ((HalIoWritePartitionTable == HalpXboxIoWritePartitionTable) << 3);
}
ULONG HalpXwnSavedPartitionMask(VOID)
{
    return (NtoskrnlExamineMBR != NULL && NtoskrnlExamineMBR != HalExamineMBR) |
           ((NtoskrnlIoReadPartitionTable != NULL && NtoskrnlIoReadPartitionTable != HalIoReadPartitionTable) << 1) |
           ((NtoskrnlIoSetPartitionInformation != NULL && NtoskrnlIoSetPartitionInformation != HalIoSetPartitionInformation) << 2) |
           ((NtoskrnlIoWritePartitionTable != NULL && NtoskrnlIoWritePartitionTable != HalIoWritePartitionTable) << 3);
}
#endif
