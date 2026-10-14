/* Experimental Windows 2000 support, GPL-2.0-or-later.
 * Only linked into nvnetnt5. DriverEntry rejects multiprocessor systems.
 */
#include "nvnet.h"

static VOID NTAPI
NvNetNt5DpcBarrier(PKDPC Dpc, PVOID Context, PVOID Argument1, PVOID Argument2)
{
    KeSetEvent((PKEVENT)Context, IO_NO_INCREMENT, FALSE);
}

VOID
NvNetNt5FlushDpcs(VOID)
{
    KEVENT Event;
    KDPC Dpc;
    /* On a single CPU a low-importance tail entry runs after all DPCs already
     * queued. The waiter cannot resume until this DPC has returned. Producers
     * are disabled by NvNetStopAdapter before this barrier is inserted. */
    ASSERT(KeGetCurrentIrql() == PASSIVE_LEVEL);
    KeInitializeEvent(&Event, NotificationEvent, FALSE);
    KeInitializeDpc(&Dpc, NvNetNt5DpcBarrier, &Event);
    KeSetImportanceDpc(&Dpc, LowImportance);
    KeInsertQueueDpc(&Dpc, NULL, NULL);
    KeWaitForSingleObject(&Event, Executive, KernelMode, FALSE, NULL);
}

VOID NTAPI
NvNetNt5SendPackets(NDIS_HANDLE Context, PPNDIS_PACKET Packets, UINT Count)
{
    UINT Index;
    for (Index = 0; Index < Count; ++Index)
    {
        NDIS_STATUS Status = MiniportSend(Context, Packets[Index], 0);
        NDIS_SET_PACKET_STATUS(Packets[Index], Status);
        /* NDIS requeues this packet and the untouched remainder, preserving
         * order. None of them has been accepted by the hardware yet. */
        if (Status == NDIS_STATUS_RESOURCES) break;
    }
}
