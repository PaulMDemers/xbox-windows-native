/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only observational snapshots. No GPU writes, RAMIN reads or ownership.
 * Existing miniport owns Control mapping; never remap, retain or expose pointers.
 */
#include <ntddk.h>
#include "registers.h"
VOID NTAPI XwnVideoTrace(ULONG,ULONG,ULONG,ULONG);
static volatile LONG XgnSeen[2];
VOID NTAPI XgnSnapshot(PVOID Control,ULONG Length,ULONG Phase)
{
    ULONG irql=KeGetCurrentIrql();
#if XWN_GPU_SNAPSHOT
    ULONG i,value,checksum=0;
#endif
    if(Phase>=2) {XwnVideoTrace(21403,Phase,1,irql);return;}
    if(irql!=PASSIVE_LEVEL || !Control || ((ULONG_PTR)Control&3) || Length!=XGN_MAPPED_LENGTH)
    {XwnVideoTrace(21403,Phase,2,irql);return;}
    /* CPU-only once gate. It does not stop GPU work or synchronize register state. */
    if(InterlockedCompareExchange(&XgnSeen[Phase],1,0)) return;
    XwnVideoTrace(21400,Phase,XWN_GPU_SNAPSHOT,irql);
#if XWN_GPU_SNAPSHOT
    for(i=0;i<XGN_REGISTER_COUNT;i++) {
        if((XgnOffsets[i]&3) || XgnOffsets[i]>Length-sizeof(ULONG))
        {XwnVideoTrace(21403,Phase,3,i);return;}
        value=READ_REGISTER_ULONG((PULONG)((PUCHAR)Control+XgnOffsets[i]));
        checksum ^= value ^ XgnOffsets[i];
        XwnVideoTrace(21401,Phase,XgnOffsets[i],value);
    }
    XwnVideoTrace(21402,Phase,XGN_REGISTER_COUNT,checksum);
#endif
}
