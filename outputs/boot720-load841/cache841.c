/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache841.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE841_ROW;
static volatile CACHE841_ROW Rows841[16];
static volatile LONG Sequence841;
static KBUGCHECK_CALLBACK_RECORD Callback841;

static char *hex841(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback841(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence841, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN841: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE841_ROW *r=&Rows841[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex841(p,n);p=hex841(p,r->Site);
        p=hex841(p,r->OffsetHigh);p=hex841(p,r->OffsetLow);
        p=hex841(p,r->Length);p=hex841(p,r->SizeHigh);p=hex841(p,r->SizeLow);p=hex841(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache841Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback841);
    if (!KeRegisterBugCheckCallback(&Callback841,callback841,(PVOID)Rows841,sizeof(Rows841),(PUCHAR)"XWN841"))
        KeBugCheckEx(0xE8410002,0,0,0,0);
}
static VOID check841(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence841);
    volatile CACHE841_ROW *r=&Rows841[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8410003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache841_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8410001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache841Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check841(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache841Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check841(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
