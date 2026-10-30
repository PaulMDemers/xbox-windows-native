/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Owned diagnostic: record cache requests and stop before an out-of-extent map.
 * This is not a filesystem repair. No allocation/name/chain policy is changed.
 * All code/data here stays resident; bugcheck callback reads only this ring. */
#include "vfat.h"
#include "cache838.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);

typedef struct {
    ULONG Sequence, Site, OffsetLow, OffsetHigh, Length, SizeLow, SizeHigh, Flags;
} CACHE838_ROW;
static volatile CACHE838_ROW Rows838[16];
static volatile LONG Sequence838;
static KBUGCHECK_CALLBACK_RECORD Callback838;

static char *hex838(char *p, ULONG v)
{
    static const char digits[]="0123456789ABCDEF";
    int i;
    for (i=28;i>=0;i-=4) *p++=digits[(v>>i)&15];
    *p++=' ';
    return p;
}
static VOID NTAPI callback838(PVOID Buffer, ULONG Length)
{
    ULONG end=(ULONG)Sequence838, n, first=end>3?end-3:1;
    char line[112], *p;
    UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nXWN838: sequence site offsetHi offsetLo length sizeHi sizeLo flags\n");
    for (n=first;n<=end;n++) {
        volatile CACHE838_ROW *r=&Rows838[n&15];
        if(r->Sequence!=n) continue;
        p=line;p=hex838(p,n);p=hex838(p,r->Site);
        p=hex838(p,r->OffsetHigh);p=hex838(p,r->OffsetLow);
        p=hex838(p,r->Length);p=hex838(p,r->SizeHigh);p=hex838(p,r->SizeLow);p=hex838(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Cache838Initialize(VOID)
{
    KeInitializeCallbackRecord(&Callback838);
    if (!KeRegisterBugCheckCallback(&Callback838,callback838,(PVOID)Rows838,sizeof(Rows838),(PUCHAR)"XWN838"))
        KeBugCheckEx(0xE8380002,0,0,0,0);
}
static VOID check838(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length)
{
    PVFATFCB fcb=(PVFATFCB)FileObject->FsContext;
    ULONG n=(ULONG)InterlockedIncrement(&Sequence838);
    volatile CACHE838_ROW *r=&Rows838[n&15];
    LARGE_INTEGER size;
    if (!fcb) KeBugCheckEx(0xE8380003,Site,(ULONG_PTR)FileObject,0,0);
    size=fcb->RFCB.FileSize;
    r->Sequence=0;r->Site=Site;r->OffsetLow=Offset->LowPart;r->OffsetHigh=Offset->HighPart;
    r->Length=Length;r->SizeLow=size.LowPart;r->SizeHigh=size.HighPart;r->Flags=fcb->Flags;
    InterlockedExchange((PLONG)&r->Sequence,(LONG)n);
    if (cache838_bad(Offset->QuadPart,Length,size.QuadPart))
        KeBugCheckEx(0xE8380001,Site,Offset->LowPart,Length,size.LowPart);
}
BOOLEAN Cache838Map(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check838(Site,FileObject,Offset,Length);
    return CcMapData(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
BOOLEAN Cache838Pin(ULONG Site,PFILE_OBJECT FileObject,PLARGE_INTEGER Offset,ULONG Length,ULONG Flags,PVOID *Bcb,PVOID *Buffer)
{
    check838(Site,FileObject,Offset,Length);
    return CcPinRead(FileObject,Offset,Length,Flags,Bcb,Buffer);
}
