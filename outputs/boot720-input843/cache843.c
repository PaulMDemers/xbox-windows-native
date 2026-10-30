/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache843.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE843_ROW;
static volatile CACHE843_ROW Rows843[16];
static volatile LONG Sequence843;
static KBUGCHECK_CALLBACK_RECORD Callback843;

static char *hex843(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback843(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence843, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN843: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE843_ROW *r=&Rows843[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex843(p,n);p=hex843(p,r->Site);
        p=hex843(p,r->OffsetHigh);p=hex843(p,r->OffsetLow);
        p=hex843(p,r->Length);p=hex843(p,r->SizeHigh);p=hex843(p,r->SizeLow);p=hex843(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache843Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback843);
    if (!KeRegisterBugCheckCallback(&Callback843,callback843,(PVOID)Rows843,sizeof(Rows843),(PUCHAR)"XWN843"))
        KeBugCheckEx(0xE8430002,0,0,0,0);
}
static VOID check843(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence843);
    volatile CACHE843_ROW *r=&Rows843[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8430003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache843_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8430001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache843Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check843(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache843Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check843(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
