from pathlib import Path
src=Path('/home/paul/xbox-windows-native/sources/reactos-extended')
kit=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-extended-partitions')
(src/'sdk/include/reactos/xboxpart.h').write_bytes((kit/'xboxpart.h').read_bytes())
p=src/'boot/freeldr/freeldr/disk/part_brfr.c';s=p.read_text();s=s.replace('#ifndef _M_ARM','#ifndef _M_ARM\n#include <xboxpart.h>',1)
needle='    ASSERT(SectorSize >= 512);'
s=s.replace(needle,'''    XWN_XBOX_PARTITION Parts[XWN_XBOX_MAX_PARTITIONS];
    GEOMETRY Geometry;
    unsigned int Count;
    int TableStatus;

    ASSERT(SectorSize >= 512);''',1)
needle='    /* Get partition entry of an Xbox-standard BRFR partitioned disk */'
s=s.replace(needle,'''    /* Extended metadata is authoritative when present, including E: size. */
    if (SectorSize != 512 || !MachDiskGetDriveGeometry(DriveNumber, &Geometry) ||
        !MachDiskReadLogicalSectors(DriveNumber, 0, 1, DiskReadBuffer))
        return FALSE;
    TableStatus = XwnXboxParsePartitionTable(DiskReadBuffer, SectorSize,
                                           Geometry.Sectors, Parts, &Count);
    if (TableStatus == XWN_XBOX_TABLE_INVALID)
        return FALSE;
    if (TableStatus == XWN_XBOX_TABLE_VALID)
    {
        if (PartitionNumber < 1 || PartitionNumber > Count) return FALSE;
        RtlZeroMemory(PartitionEntry, sizeof(*PartitionEntry));
        PartitionEntry->StartingOffset.QuadPart = (ULONGLONG)Parts[PartitionNumber-1].Start * SectorSize;
        PartitionEntry->PartitionLength.QuadPart = (ULONGLONG)Parts[PartitionNumber-1].Count * SectorSize;
        PartitionEntry->PartitionNumber = PartitionNumber;
        PartitionEntry->PartitionType = PARTITION_FAT32;
        PartitionEntry->BootIndicator = (PartitionNumber == FATX_DATA_PARTITION);
        PartitionEntry->RecognizedPartition = TRUE;
        return TRUE;
    }

'''+needle,1)
p.write_text(s)
p=src/'hal/halx86/xbox/part_xbox.c';s=p.read_text().replace('#include <internal/tag.h>','#include <internal/tag.h>\n#include <xboxpart.h>')
needle='static NTSTATUS FASTCALL\nHalpXboxIoReadPartitionTable'
helper='''/* Require an exact device length before trusting extended on-disk extents.
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
    *TableStatus = XWN_XBOX_TABLE_INVALID;
    if (SectorSize != 512) return STATUS_NOT_SUPPORTED;
    Buffer = ExAllocatePoolWithTag(PagedPool, SectorSize, TAG_HAL_XBOX);
    if (!Buffer) return STATUS_INSUFFICIENT_RESOURCES;
    Offset.QuadPart = 0;
    Status = HalpXboxReadSector(Device, SectorSize, &Offset, Buffer);
    if (!NT_SUCCESS(Status)) goto Done;
    /* The first parse only detects absence. An unknown capacity cannot validate. */
    *TableStatus = XwnXboxParsePartitionTable(Buffer, SectorSize, 0, Parts, Count);
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
    if (!NT_SUCCESS(Status)) goto Done;
    if (Io.Information < sizeof(Length) || Length.Length.QuadPart <= 0 ||
        (Length.Length.QuadPart & 511))
    { Status = STATUS_DISK_CORRUPT_ERROR; goto Done; }
    *TableStatus = XwnXboxParsePartitionTable(Buffer, SectorSize,
                         (ULONGLONG)Length.Length.QuadPart / 512, Parts, Count);
    if (*TableStatus != XWN_XBOX_TABLE_VALID) Status = STATUS_DISK_CORRUPT_ERROR;
Done:
    ExFreePoolWithTag(Buffer, TAG_HAL_XBOX);
    return Status;
}

'''
s=s.replace(needle,helper+needle,1)
needle='    PPARTITION_INFORMATION PartInfo;'
s=s.replace(needle,needle+'''
    XWN_XBOX_PARTITION Parts[XWN_XBOX_MAX_PARTITIONS];
    unsigned int PartCount = XBOX_PARTITION_COUNT;
    int TableStatus;''',1)
needle='    *PartitionBuffer = (PDRIVE_LAYOUT_INFORMATION)ExAllocatePoolWithTag('
s=s.replace(needle,'''    Status = HalpXboxReadExtendedLayout(DeviceObject, SectorSize, Parts,
                                        &PartCount, &TableStatus);
    if (!NT_SUCCESS(Status)) return Status;
    if (TableStatus == XWN_XBOX_TABLE_ABSENT) PartCount = XBOX_PARTITION_COUNT;

'''+needle,1)
s=s.replace('XBOX_PARTITION_COUNT * sizeof(PARTITION_INFORMATION)','PartCount * sizeof(PARTITION_INFORMATION)',1).replace('(*PartitionBuffer)->PartitionCount = XBOX_PARTITION_COUNT','(*PartitionBuffer)->PartitionCount = PartCount',1).replace('Part < XBOX_PARTITION_COUNT','Part < PartCount',1)
s=s.replace('XboxPartitions[Part].SectorStart *','(TableStatus == XWN_XBOX_TABLE_VALID ? Parts[Part].Start : XboxPartitions[Part].SectorStart) *',1).replace('XboxPartitions[Part].SectorCount *','(TableStatus == XWN_XBOX_TABLE_VALID ? Parts[Part].Count : XboxPartitions[Part].SectorCount) *',1).replace('PartInfo->PartitionType = XboxPartitions[Part].PartitionType;','PartInfo->PartitionType = TableStatus == XWN_XBOX_TABLE_VALID ? PARTITION_FAT32 : XboxPartitions[Part].PartitionType;',1)
p.write_text(s)
print('Extended table parser installed in isolated 0059 source branch.')
