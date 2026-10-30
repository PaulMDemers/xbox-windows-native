/* SPDX-License-Identifier: GPL-2.0-or-later */
/* RAM-only observation of display image opens/reads and image-load notifications.
 * No return status, buffer, configuration, PCI or display-state changes. */
#include "vfat.h"
NTHALAPI VOID NTAPI HalDisplayString(PCH String);
typedef struct {
    volatile LONG Opens, Reads, Images;
    ULONG OpenStatus, ReadStatus, Offset, Requested, Returned, Size, Flags, Tail;
} LOAD841_ROW;
static LOAD841_ROW LoadRows841[3];
static KBUGCHECK_CALLBACK_RECORD LoadCallback841;
static NTSTATUS NotifyStatus841;
static const WCHAR *Names841[]={L"xboxvnt5.sys",L"videoprt.sys",L"xwnown.dll"};
static ULONG identify841(PUNICODE_STRING Name)
{
    ULONG i,j,n,start;
    if (!Name || !Name->Buffer || (Name->Length&1)) return 3;
    n=Name->Length/sizeof(WCHAR);
    for(i=0;i<3;i++) {
        ULONG count=0;while(Names841[i][count])count++;
        if(n<count)continue;
        start=n-count;
        if(start && Name->Buffer[start-1]!=L'\\' && Name->Buffer[start-1]!=L'/')continue;
        for(j=0;j<count;j++) {
            WCHAR c=Name->Buffer[start+j];if(c>=L'A'&&c<=L'Z')c+=L'a'-L'A';
            if(c!=Names841[i][j])break;
        }
        if(j==count)return i;
    }
    return 3;
}
static VOID NTAPI image841(PUNICODE_STRING Name,HANDLE ProcessId,PIMAGE_INFO Info)
{
    ULONG i=identify841(Name);
    if(i<3 && !ProcessId && Info && Info->SystemModeImage)
        InterlockedIncrement(&LoadRows841[i].Images);
}
VOID Load841Open(PFILE_OBJECT File, NTSTATUS Status)
{
    ULONG i;if(!File)return;i=identify841(&File->FileName);if(i>=3)return;
    LoadRows841[i].OpenStatus=Status;InterlockedIncrement(&LoadRows841[i].Opens);
}
VOID Load841Read(PVFAT_IRP_CONTEXT Context,NTSTATUS Status,ULONG Requested,LARGE_INTEGER Offset)
{
    ULONG i;PFILE_OBJECT file=Context->FileObject;PVFATFCB fcb;LOAD841_ROW *r;
    if(!file)return;fcb=file->FsContext;i=identify841(&file->FileName);
    /* Cache-manager stream file objects may have no FileName. */
    if(i>=3 && fcb)i=identify841(&fcb->PathNameU);
    if(i>=3)return;r=&LoadRows841[i];
    r->ReadStatus=Status;r->Offset=Offset.LowPart;r->Requested=Requested;
    r->Returned=NT_SUCCESS(Status)?(ULONG)Context->Irp->IoStatus.Information:0;
    r->Flags=Context->Irp->Flags;r->Size=fcb?fcb->RFCB.FileSize.LowPart:0;r->Tail=0xffffffff;
    if(fcb && NT_SUCCESS(Status) && r->Returned<=Requested && (Context->Irp->Flags&IRP_PAGING_IO) &&
       Offset.QuadPart<=fcb->RFCB.FileSize.QuadPart &&
       fcb->RFCB.FileSize.QuadPart-Offset.QuadPart<r->Returned) {
        PUCHAR p=VfatGetUserBuffer(Context->Irp,TRUE);
        if(p)r->Tail=p[(ULONG)(fcb->RFCB.FileSize.QuadPart-Offset.QuadPart)];
    }
    InterlockedIncrement(&r->Reads);
}
static char *hex841(char *p,ULONG v)
{
    static const char d[]="0123456789ABCDEF";int i;
    for(i=28;i>=0;i-=4)*p++=d[(v>>i)&15];*p++=' ';return p;
}
static VOID NTAPI dump841(PVOID Buffer,ULONG Length)
{
    ULONG i;char line[120],*p;UNREFERENCED_PARAMETER(Buffer);UNREFERENCED_PARAMETER(Length);
    HalDisplayString("\nLOAD841 files: 0=xboxvnt5 1=videoprt 2=xwnown; notify-status ");
    p=hex841(line,NotifyStatus841);*p++='\n';*p=0;HalDisplayString(line);
    HalDisplayString("id opens openStatus reads images readStatus fileSize flags\n");
    for(i=0;i<3;i++) {LOAD841_ROW *r=&LoadRows841[i];p=line;
        p=hex841(p,i);p=hex841(p,r->Opens);p=hex841(p,r->OpenStatus);p=hex841(p,r->Reads);
        p=hex841(p,r->Images);p=hex841(p,r->ReadStatus);p=hex841(p,r->Size);p=hex841(p,r->Flags);
        *p++='\n';*p=0;HalDisplayString(line);
    }
    HalDisplayString("id lastOffset requested returned EOFbyte(FFFFFFFF=not observed)\n");
    for(i=0;i<3;i++) {LOAD841_ROW *r=&LoadRows841[i];p=line;
        p=hex841(p,i);p=hex841(p,r->Offset);p=hex841(p,r->Requested);p=hex841(p,r->Returned);p=hex841(p,r->Tail);
        *p++='\n';*p=0;HalDisplayString(line);
    }
}
VOID Load841Initialize(VOID)
{
    ULONG i;for(i=0;i<3;i++)LoadRows841[i].Tail=0xffffffff;
    NotifyStatus841=PsSetLoadImageNotifyRoutine(image841);
    KeInitializeCallbackRecord(&LoadCallback841);
    if(!KeRegisterBugCheckCallback(&LoadCallback841,dump841,LoadRows841,sizeof(LoadRows841),(PUCHAR)"LOAD841"))
        KeBugCheckEx(0xE8410004,0,0,0,0);
}
