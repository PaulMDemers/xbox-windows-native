/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache839.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE839_ROW;
static volatile CACHE839_ROW Rows839[16];
static volatile LONG Sequence839;
static KBUGCHECK_CALLBACK_RECORD Callback839;

static char *hex839(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback839(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence839, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN839: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE839_ROW *r=&Rows839[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex839(p,n);p=hex839(p,r->Site);
        p=hex839(p,r->OffsetHigh);p=hex839(p,r->OffsetLow);
        p=hex839(p,r->Length);p=hex839(p,r->SizeHigh);p=hex839(p,r->SizeLow);p=hex839(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache839Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback839);
    if (!KeRegisterBugCheckCallback(&Callback839,callback839,(PVOID)Rows839,sizeof(Rows839),(PUCHAR)"XWN839"))
        KeBugCheckEx(0xE8390002,0,0,0,0);
}
static VOID check839(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence839);
    volatile CACHE839_ROW *r=&Rows839[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8390003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache839_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8390001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache839Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check839(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache839Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check839(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
