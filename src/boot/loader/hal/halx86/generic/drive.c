/*
 * PROJECT:         ReactOS HAL
 * LICENSE:         GPL - See COPYING in the top level directory
 * FILE:            hal/halx86/generic/drive.c
 * PURPOSE:         I/O HAL Routines for Disk Access
 * PROGRAMMERS:     Alex Ionescu (alex.ionescu@reactos.org)
 */

/* INCLUDES ******************************************************************/

#include <hal.h>

#include <ntdddisk.h>

#define NDEBUG
#include <debug.h>

/* Windows 2000 exports these stdcall wrappers from HAL and retains the
 * fastcall implementations in HalDispatchTable. Use the dispatch entries,
 * including the Xbox partition hooks, instead of importing newer kernel
 * wrappers. Verified against the supplied 2195 HAL and kernel binaries. */
#ifdef XBOX_NT5_HAL
#define IoAssignDriveLetters HALDISPATCH->HalIoAssignDriveLetters
#define IoReadPartitionTable HALDISPATCH->HalIoReadPartitionTable
#define IoSetPartitionInformation HALDISPATCH->HalIoSetPartitionInformation
#define IoWritePartitionTable HALDISPATCH->HalIoWritePartitionTable
#endif

/* FUNCTIONS *****************************************************************/

VOID
NTAPI
HalpAssignDriveLetters(IN struct _LOADER_PARAMETER_BLOCK *LoaderBlock,
                       IN PSTRING NtDeviceName,
                       OUT PUCHAR NtSystemPath,
                       OUT PSTRING NtSystemPathString)
{
    /* Call the kernel */
    IoAssignDriveLetters(LoaderBlock,
                         NtDeviceName,
                         NtSystemPath,
                         NtSystemPathString);
}

NTSTATUS
NTAPI
HalpReadPartitionTable(IN PDEVICE_OBJECT DeviceObject,
                       IN ULONG SectorSize,
                       IN BOOLEAN ReturnRecognizedPartitions,
                       IN OUT PDRIVE_LAYOUT_INFORMATION *PartitionBuffer)
{
    /* Call the kernel */
    return IoReadPartitionTable(DeviceObject,
                                SectorSize,
                                ReturnRecognizedPartitions,
                                PartitionBuffer);
}

NTSTATUS
NTAPI
HalpWritePartitionTable(IN PDEVICE_OBJECT DeviceObject,
                        IN ULONG SectorSize,
                        IN ULONG SectorsPerTrack,
                        IN ULONG NumberOfHeads,
                        IN PDRIVE_LAYOUT_INFORMATION PartitionBuffer)
{
    /* Call the kernel */
    return IoWritePartitionTable(DeviceObject,
                                 SectorSize,
                                 SectorsPerTrack,
                                 NumberOfHeads,
                                 PartitionBuffer);
}

NTSTATUS
NTAPI
HalpSetPartitionInformation(IN PDEVICE_OBJECT DeviceObject,
                            IN ULONG SectorSize,
                            IN ULONG PartitionNumber,
                            IN ULONG PartitionType)
{
    /* Call the kernel */
    return IoSetPartitionInformation(DeviceObject,
                                     SectorSize,
                                     PartitionNumber,
                                     PartitionType);
}
/* EOF */
