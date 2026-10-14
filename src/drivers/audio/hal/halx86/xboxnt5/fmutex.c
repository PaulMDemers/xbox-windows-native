/*
 * PROJECT:     Experimental Windows 2000 Xbox HAL
 * LICENSE:     GPL-2.0-or-later
 * PURPOSE:     HAL-owned fast mutexes, using NT 5.0 kernel exports.
 * Derived from ReactOS ntoskrnl/include/internal/ex.h fast-mutex algorithms.
 * Runtime/ABI validation against Windows 2000 remains required.
 */
#include <hal.h>
#undef ExAcquireFastMutex
#undef ExReleaseFastMutex
#undef ExTryToAcquireFastMutex

/* The NT5 x86 FAST_MUTEX ABI; never use a version-specific KTHREAD field. */
C_ASSERT(NTDDI_VERSION == NTDDI_WIN2K);
C_ASSERT(HAL_DISPATCH_VERSION == 2);
C_ASSERT(HAL_PRIVATE_DISPATCH_VERSION == 1);
C_ASSERT(sizeof(HAL_DISPATCH) == 0x44);
C_ASSERT(sizeof(HAL_PRIVATE_DISPATCH) == 0x30);
C_ASSERT(FIELD_OFFSET(HAL_DISPATCH, HalIoAssignDriveLetters) == 0x18);
C_ASSERT(FIELD_OFFSET(HAL_DISPATCH, HalIoReadPartitionTable) == 0x1c);
C_ASSERT(FIELD_OFFSET(HAL_DISPATCH, HalIoSetPartitionInformation) == 0x20);
C_ASSERT(FIELD_OFFSET(HAL_DISPATCH, HalIoWritePartitionTable) == 0x24);
C_ASSERT(sizeof(FAST_MUTEX) == 32);
C_ASSERT(FIELD_OFFSET(FAST_MUTEX, Count) == 0);
C_ASSERT(FIELD_OFFSET(FAST_MUTEX, Owner) == 4);
C_ASSERT(FIELD_OFFSET(FAST_MUTEX, Contention) == 8);
C_ASSERT(FIELD_OFFSET(FAST_MUTEX, Event) == 12);
C_ASSERT(FIELD_OFFSET(FAST_MUTEX, OldIrql) == 28);

VOID FASTCALL
ExAcquireFastMutex(PFAST_MUTEX Mutex)
{
    KIRQL OldIrql;
    KeRaiseIrql(APC_LEVEL, &OldIrql);
    if (InterlockedDecrement(&Mutex->Count) != 0)
    {
        InterlockedIncrement((PLONG)&Mutex->Contention);
        KeWaitForSingleObject(&Mutex->Event, Executive, KernelMode, FALSE, NULL);
    }
    Mutex->Owner = KeGetCurrentThread();
    Mutex->OldIrql = OldIrql;
}

VOID FASTCALL
ExReleaseFastMutex(PFAST_MUTEX Mutex)
{
    KIRQL OldIrql = (KIRQL)Mutex->OldIrql;
    Mutex->Owner = NULL;
    if (InterlockedIncrement(&Mutex->Count) <= 0)
        KeSetEventBoostPriority(&Mutex->Event, NULL);
    KeLowerIrql(OldIrql);
}

BOOLEAN FASTCALL
ExTryToAcquireFastMutex(PFAST_MUTEX Mutex)
{
    KIRQL OldIrql;
    KeRaiseIrql(APC_LEVEL, &OldIrql);
    if (InterlockedCompareExchange(&Mutex->Count, 0, 1) == 1)
    {
        Mutex->Owner = KeGetCurrentThread();
        Mutex->OldIrql = OldIrql;
        return TRUE;
    }
    KeLowerIrql(OldIrql);
    return FALSE;
}
