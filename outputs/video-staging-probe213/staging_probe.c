/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only allocation/copy/release probe. NO DMA or MMIO. Never exposes
 * an allocation address as a GPU capability. The fixed UC crash view is untouched.
 */
#include <ntddk.h>
#if XWN_STAGING_PROBE
#define XGT_U32 ULONG
#define XGT_U64 ULONGLONG
#define XGT_I32 LONG
#include "transfer_plan.h"
#endif
VOID NTAPI XwnVideoTrace(ULONG,ULONG,ULONG,ULONG);
#define BYTES 16384u
BOOLEAN NTAPI XgtNativeProbe(VOID)
{
#if XWN_STAGING_PROBE
    PHYSICAL_ADDRESS low,high,boundary,physical,at;
    PUCHAR memory,source,destination,stage;
    XGT_LAYOUT a={64,16,256,4096},b={64,16,272,4352};
    XGT_RECT rect={3,2,61,15};XGT_PLAN plan;XGT_STRIP strip;
    ULONG i,row,col,cursor=0,checks=0,tiles=0,reason=0;
    BOOLEAN passed=FALSE;
    XwnVideoTrace(21300,1,BYTES,KeGetCurrentIrql());
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL) return FALSE;
    low.QuadPart=0x100000;high.QuadPart=0x03bfffff;boundary.QuadPart=0;
    memory=MmAllocateContiguousMemorySpecifyCache(BYTES,low,high,boundary,MmNonCached);
    if(!memory) { XwnVideoTrace(21301,0,0,1);return FALSE; }
    physical=MmGetPhysicalAddress(memory);
    XwnVideoTrace(21301,physical.LowPart,physical.HighPart,0);
    if(physical.QuadPart<low.QuadPart || physical.QuadPart+BYTES-1>high.QuadPart ||
       (physical.LowPart&4095)) { reason=2;goto done; }
    for(i=0;i<BYTES;i+=4096) {
        at=MmGetPhysicalAddress(memory+i);checks++;
        if(at.QuadPart!=physical.QuadPart+i) {reason=3;goto done;}
    }
    at=MmGetPhysicalAddress(memory+BYTES-1);checks++;
    if(at.QuadPart!=physical.QuadPart+BYTES-1) {reason=4;goto done;}
    RtlFillMemory(memory,BYTES,0xcd);
    source=memory+64;destination=memory+4224;stage=memory+8640;
    for(row=0;row<a.height;row++) for(col=0;col<a.pitch;col++)
        source[row*a.pitch+col]=(UCHAR)(row*17+col*7);
    if(!XgtPlan(&plan,&a,&b,&rect,1024)) {reason=5;goto done;}
    while(XgtStrip(&plan,cursor,&strip)) {
        if(++tiles>16 || strip.next_row<=cursor) {reason=6;goto done;}
        for(row=0;row<strip.rows;row++) RtlCopyMemory(stage+row*strip.row_bytes,
            source+strip.source_offset+row*a.pitch,strip.row_bytes);
        for(row=0;row<strip.rows;row++) RtlCopyMemory(destination+strip.destination_offset+row*b.pitch,
            stage+row*strip.row_bytes,strip.row_bytes);
        cursor=strip.next_row;
    }
    if(cursor!=13) {reason=7;goto done;}
    /* Independent destination oracle, including padding and untouched pixels. */
    for(row=0;row<b.height;row++) for(col=0;col<b.pitch;col++) {
        UCHAR expected=(row>=2 && row<15 && col>=12 && col<244)?
            (UCHAR)(row*17+col*7):0xcd;
        checks++;if(destination[row*b.pitch+col]!=expected) {reason=8;goto done;}
    }
    for(row=0;row<a.height;row++) for(col=0;col<a.pitch;col++) {
        checks++;if(source[row*a.pitch+col]!=(UCHAR)(row*17+col*7)) {reason=9;goto done;}
    }
    for(i=0;i<BYTES;i++) if(i<64 || (i>=4160 && i<4224) ||
         (i>=8576 && i<8640) || i>=9664) {
        checks++;if(memory[i]!=0xcd) {reason=10;goto done;}
    }
    passed=TRUE;
done:
    XwnVideoTrace(21302,checks,tiles,reason);
    /* No GPU can reference this buffer: none was configured or submitted.
     * This unconditional release is NOT a DMA timeout cleanup recipe. */
    MmFreeContiguousMemorySpecifyCache(memory,BYTES,MmNonCached);
    XwnVideoTrace(21303,passed,BYTES,KeGetCurrentIrql());
    return passed;
#else
    XwnVideoTrace(21300,0,0,KeGetCurrentIrql());
    return TRUE;
#endif
}
