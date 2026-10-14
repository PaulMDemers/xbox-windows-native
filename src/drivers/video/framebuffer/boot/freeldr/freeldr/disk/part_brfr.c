/*
 * PROJECT:     FreeLoader
 * LICENSE:     GPL-2.0-or-later (https://spdx.org/licenses/GPL-2.0-or-later)
 * PURPOSE:     Xbox (BRFR) partitioning scheme support
 * COPYRIGHT:   Copyright 2004 Gé van Geldorp <gvg@reactos.org>
 *              Copyright 2019 Stanislav Motylkov <x86corez@gmail.com>
 */

#ifndef _M_ARM
#include <xboxpart.h>
// #include <freeldr.h>

/* BRFR signature at disk offset 0x600 (== 3 * 0x200) */
#define XBOX_SIGNATURE_SECTOR 3
#define XBOX_SIGNATURE        ('B' | ('R' << 8) | ('F' << 16) | ('R' << 24))

/* Default hardcoded partition number to boot from Xbox disk */
#define FATX_DATA_PARTITION 1

static struct
{
    ULONG SectorStart;
    ULONG SectorCount;
    UCHAR PartitionType;
} XboxPartitions[] =
{
    /* This is in the \Device\Harddisk0\Partition.. order used by the Xbox kernel */
    { 0x0055F400, 0x0098F800, PARTITION_FAT32  }, /* Store , E: */
    { 0x00465400, 0x000FA000, PARTITION_FAT_16 }, /* System, C: */
    { 0x00000400, 0x00177000, PARTITION_FAT_16 }, /* Cache1, X: */
    { 0x00177400, 0x00177000, PARTITION_FAT_16 }, /* Cache2, Y: */
    { 0x002EE400, 0x00177000, PARTITION_FAT_16 }  /* Cache3, Z: */
};

static BOOLEAN
DiskIsBrfr(
    _In_ UCHAR DriveNumber)
{
    /* Read the Xbox-specific sector */
    if (!MachDiskReadLogicalSectors(DriveNumber, XBOX_SIGNATURE_SECTOR, 1, DiskReadBuffer))
        return FALSE; /* Partition does not exist */

    /* Verify the magic Xbox signature */
    return (*((PULONG)DiskReadBuffer) == XBOX_SIGNATURE);
}

BOOLEAN
DiskGetBrfrPartitionEntry(
    _In_ UCHAR DriveNumber,
    _In_ ULONG SectorSize,
    _In_ ULONG PartitionNumber,
    _Out_ PPARTITION_INFORMATION PartitionEntry)
{
    XWN_XBOX_PARTITION Parts[XWN_XBOX_MAX_PARTITIONS];
    GEOMETRY Geometry;
    unsigned int Count;
    int TableStatus;

    ASSERT(SectorSize >= 512);

    if (!DiskIsBrfr(DriveNumber))
        return FALSE; /* No magic Xbox partitions */

    /* Extended metadata is authoritative when present, including E: size. */
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

    /* Get partition entry of an Xbox-standard BRFR partitioned disk */
    if (!(1 <= PartitionNumber && PartitionNumber <= RTL_NUMBER_OF(XboxPartitions)))
        return FALSE; /* Partition does not exist */

    /* Convert to standard-style entry */
    PartitionEntry->StartingOffset.QuadPart  = (ULONGLONG)XboxPartitions[PartitionNumber - 1].SectorStart * SectorSize;
    PartitionEntry->PartitionLength.QuadPart = (ULONGLONG)XboxPartitions[PartitionNumber - 1].SectorCount * SectorSize;
    PartitionEntry->HiddenSectors = 0;
    PartitionEntry->PartitionNumber = PartitionNumber;
    PartitionEntry->PartitionType = XboxPartitions[PartitionNumber - 1].PartitionType;
    PartitionEntry->BootIndicator = (PartitionNumber == FATX_DATA_PARTITION);
    PartitionEntry->RecognizedPartition = TRUE;
    PartitionEntry->RewritePartition = FALSE;

    return TRUE;
}

#endif
