/* SPDX-License-Identifier: MIT
 * Included only by the native NT5 free UP HAL reboot translation unit.
 */
#include "xwn-smbus-broker.h"
#if defined(CONFIG_SMP) || defined(_SMP_)
#error The terminal takeover contract is single-processor only
#endif
static volatile LONG HalpSmbusOwner;
static volatile xb_reply HalpSmbusTerminalResult;
static unsigned HalpSmbusRead(void *Context,unsigned Offset)
{
    UNREFERENCED_PARAMETER(Context);
    if(Offset==0)return READ_PORT_USHORT((PUSHORT)SMB_GLOBAL_STATUS);
    return READ_PORT_UCHAR((PUCHAR)(SMB_IO_BASE+Offset));
}
static void HalpSmbusWrite(void *Context,unsigned Offset,unsigned Value)
{
    UNREFERENCED_PARAMETER(Context);
    WRITE_PORT_UCHAR((PUCHAR)(SMB_IO_BASE+Offset),(UCHAR)Value);
}
static void HalpSmbusDelay(void *Context)
{ UNREFERENCED_PARAMETER(Context);KeStallExecutionProcessor(10); }
static long HalpSmbusCas(void *Context,long New,long Old)
{ UNREFERENCED_PARAMETER(Context);return InterlockedCompareExchange(&HalpSmbusOwner,New,Old); }
static long HalpSmbusExchange(void *Context,long New)
{ UNREFERENCED_PARAMETER(Context);return InterlockedExchange(&HalpSmbusOwner,New); }
static const xb_io HalpSmbusIo={NULL,HalpSmbusRead,HalpSmbusWrite,HalpSmbusDelay,HalpSmbusCas,HalpSmbusExchange};
/* Versioned kernel-only ABI; caller supplies writable nonpaged four-ULONG reply.
 * No pointer is retained. No direct client port access is part of this ABI.
 * Callers must be ordinary kernel threads, never interrupt/NMI callbacks.
 * The IRQL check rejects DISPATCH/high-IRQL callers; it does not detect NMI. */
NTSTATUS NTAPI XwnSmbusReadV1(ULONG Address,ULONG Command,PULONG Reply)
{
    xb_reply Result;
    if(!Reply || KeGetCurrentIrql()>APC_LEVEL)return STATUS_INVALID_PARAMETER;
    Result=xb_read(&HalpSmbusIo,Address,Command);
    Reply[0]=Result.result;Reply[1]=Result.status;Reply[2]=Result.polls;Reply[3]=Result.data;
    return STATUS_SUCCESS;
}
