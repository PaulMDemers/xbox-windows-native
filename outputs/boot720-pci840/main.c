/* PCI inventory840: reads only. Creates one owned report, returns to dashboard. */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <string.h>
#include "report-path.h"

int main(void) {
    char text[4096]="XWN-PCI-840\r\n";size_t used=strlen(text);DWORD written=0;
    /* Serialized kernel PCI API, FALSE means read. No BAR sizing writes. */
    const ULONG buses[]={0,0,1};
    const ULONG slots[]={0,30,0};
    for(unsigned device=0;device<3;device++){
        for(unsigned offset=0;offset<64;offset+=4){
            ULONG value=0xffffffff;
            HalReadWritePCISpace(buses[device],slots[device],offset,&value,4,FALSE);
            int n=snprintf(text+used,sizeof(text)-used,"PCI %lu %lu %02x %08lx\r\n",
                buses[device],slots[device],offset,value);
            if(n<0||(size_t)n>=sizeof(text)-used){Sleep(1000);XReboot();return 1;}
            used+=(size_t)n;
        }
    }
    const char end[]="COMPLETE 840\r\n";
    if(used+sizeof(end)>sizeof(text)){Sleep(3000);XReboot();return 1;}
    memcpy(text+used,end,sizeof(end)-1);used+=sizeof(end)-1;
    ANSI_STRING reportName; OBJECT_ATTRIBUTES reportAttrs; IO_STATUS_BLOCK createIo={0};
    HANDLE f=NULL;
    char reportPath[256];
    if(!xwn343_report_path(XeImageFileName->Buffer,XeImageFileName->Length,reportPath,sizeof(reportPath))){debugPrint("Launch namespace refused\n");Sleep(3000);XReboot();return 1;}
    RtlInitAnsiString(&reportName,reportPath);
    InitializeObjectAttributes(&reportAttrs,&reportName,OBJ_CASE_INSENSITIVE,NULL,NULL);
    NTSTATUS createStatus=NtCreateFile(&f,GENERIC_WRITE|SYNCHRONIZE,&reportAttrs,&createIo,NULL,
        FILE_ATTRIBUTE_NORMAL,0,FILE_CREATE,FILE_NON_DIRECTORY_FILE|FILE_SYNCHRONOUS_IO_NONALERT);
    int ok=NT_SUCCESS(createStatus);
    if(ok){IO_STATUS_BLOCK io;ok=WriteFile(f,text,(DWORD)used,&written,NULL)&&written==used;
        ok=NT_SUCCESS(NtFlushBuffersFile(f,&io))&&ok;CloseHandle(f);}
    debugPrint("PCI inventory %s\n",ok?"saved":"refused");Sleep(3000);XReboot();return ok?0:1;
}
