/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache837.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE837_ROW;
static volatile CACHE837_ROW Rows837[16];
static volatile LONG Sequence837;
static KBUGCHECK_CALLBACK_RECORD Callback837;

static char *hex837(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback837(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence837, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN837: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE837_ROW *r=&Rows837[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex837(p,n);p=hex837(p,r->Site);
        p=hex837(p,r->OffsetHigh);p=hex837(p,r->OffsetLow);
        p=hex837(p,r->Length);p=hex837(p,r->SizeHigh);p=hex837(p,r->SizeLow);p=hex837(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache837Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback837);
    if (!KeRegisterBugCheckCallback(&Callback837,callback837,(PVOID)Rows837,sizeof(Rows837),(PUCHAR)"XWN837"))
        KeBugCheckEx(0xE8370002,0,0,0,0);
}
static VOID check837(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence837);
    volatile CACHE837_ROW *r=&Rows837[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8370003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache837_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8370001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache837Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check837(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache837Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check837(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
