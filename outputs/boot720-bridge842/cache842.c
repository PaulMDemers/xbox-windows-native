/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache842.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE842_ROW;
static volatile CACHE842_ROW Rows842[16];
static volatile LONG Sequence842;
static KBUGCHECK_CALLBACK_RECORD Callback842;

static char *hex842(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback842(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence842, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN842: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE842_ROW *r=&Rows842[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex842(p,n);p=hex842(p,r->Site);
        p=hex842(p,r->OffsetHigh);p=hex842(p,r->OffsetLow);
        p=hex842(p,r->Length);p=hex842(p,r->SizeHigh);p=hex842(p,r->SizeLow);p=hex842(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache842Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback842);
    if (!KeRegisterBugCheckCallback(&Callback842,callback842,(PVOID)Rows842,sizeof(Rows842),(PUCHAR)"XWN842"))
        KeBugCheckEx(0xE8420002,0,0,0,0);
}
static VOID check842(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence842);
    volatile CACHE842_ROW *r=&Rows842[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8420003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache842_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8420001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache842Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check842(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache842Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check842(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
