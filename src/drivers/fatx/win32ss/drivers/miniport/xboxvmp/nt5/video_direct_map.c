/* SPDX-License-Identifier: GPL-2.0-or-later
 * Single Xbox framebuffer mapping, owned by this miniport. Reserved RAM is not
 * a PCI bus address. Keep it noncached like the loader and native boot display.
 */
#include <ntddk.h>
#include <winerror.h>

#define FRAMEBUFFER_BYTES 0x00400000
static FAST_MUTEX MappingLock;
static BOOLEAN Initialized;
static PVOID Owner, Mapping;
static ULONG RamOffset, References;

VOID NTAPI XwnDirectInitialize(VOID)
{
    ExInitializeFastMutex(&MappingLock);
    Initialized = TRUE;
}

ULONG NTAPI XwnDirectMap(PVOID Device, ULONG Ram, PVOID *Address)
{
    PHYSICAL_ADDRESS Physical;
    ULONG Status = ERROR_INVALID_PARAMETER;
    if (!Initialized || KeGetCurrentIrql() != PASSIVE_LEVEL || !Device ||
        !Address || *Address || (Ram != 0x03C00000 && Ram != 0x07C00000))
        return Status;
    ExAcquireFastMutex(&MappingLock);
    if (Mapping)
    {
        if (Owner == Device && RamOffset == Ram && References != MAXULONG)
        {
            ++References;
            *Address = Mapping;
            Status = ERROR_SUCCESS;
        }
    }
    else
    {
        Physical.QuadPart = Ram;
        Mapping = MmMapIoSpace(Physical, FRAMEBUFFER_BYTES, MmNonCached);
        if (Mapping)
        {
            Owner = Device;
            RamOffset = Ram;
            References = 1;
            *Address = Mapping;
            Status = ERROR_SUCCESS;
        }
        else Status = ERROR_NOT_ENOUGH_MEMORY;
    }
    ExReleaseFastMutex(&MappingLock);
    return Status;
}

ULONG NTAPI XwnDirectUnmap(PVOID Device, PVOID Address)
{
    ULONG Status = ERROR_INVALID_PARAMETER;
    if (!Initialized || KeGetCurrentIrql() != PASSIVE_LEVEL) return Status;
    ExAcquireFastMutex(&MappingLock);
    if (Mapping && Owner == Device && Mapping == Address && References)
    {
        if (!--References)
        {
            MmUnmapIoSpace(Mapping, FRAMEBUFFER_BYTES);
            Mapping = Owner = NULL;
            RamOffset = 0;
        }
        Status = ERROR_SUCCESS;
    }
    ExReleaseFastMutex(&MappingLock);
    return Status;
}

/* Called after VideoPort's unload routine, when no surface can still use it. */
VOID NTAPI XwnDirectClose(VOID)
{
    if (!Initialized) return;
    ExAcquireFastMutex(&MappingLock);
    if (Mapping) MmUnmapIoSpace(Mapping, FRAMEBUFFER_BYTES);
    Mapping = Owner = NULL;
    RamOffset = References = 0;
    Initialized = FALSE;
    ExReleaseFastMutex(&MappingLock);
}
