/* Read-only Partition1/6 capacity query. The only write is this application's
 * CREATE_NEW report on dashboard E:. No C:, formatting or raw disk writes. */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <string.h>

static int query(const char *path, unsigned id, char *text, size_t bytes) {
    ANSI_STRING name; OBJECT_ATTRIBUTES attrs; IO_STATUS_BLOCK io={0};
    HANDLE h; FILE_FS_SIZE_INFORMATION size={0}; PARTITION_INFORMATION part={0};
    RtlInitAnsiString(&name,path);
    InitializeObjectAttributes(&attrs,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
    NTSTATUS s=NtOpenFile(&h,GENERIC_READ|SYNCHRONIZE,&attrs,&io,
        FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_SYNCHRONOUS_IO_NONALERT);
    if (!NT_SUCCESS(s)) return snprintf(text,bytes,"OPEN %u %08lx\r\n",id,(unsigned long)s);
    s=NtQueryVolumeInformationFile(h,&io,&size,sizeof(size),FileFsSizeInformation);
    NTSTATUS p=NtDeviceIoControlFile(h,NULL,NULL,NULL,&io,IOCTL_DISK_GET_PARTITION_INFO,
        NULL,0,&part,sizeof(part));
    if(p==STATUS_PENDING){p=NtWaitForSingleObject(h,FALSE,NULL);if(NT_SUCCESS(p))p=io.Status;}
    NtClose(h);
    if(!NT_SUCCESS(s)||!NT_SUCCESS(p))return snprintf(text,bytes,"QUERY %u %08lx %08lx\r\n",id,(unsigned long)s,(unsigned long)p);
    unsigned long long unit=(unsigned long long)size.BytesPerSector*size.SectorsPerAllocationUnit;
    if(!unit||size.TotalAllocationUnits.QuadPart<=0||size.AvailableAllocationUnits.QuadPart<0||
       size.AvailableAllocationUnits.QuadPart>size.TotalAllocationUnits.QuadPart)
        return snprintf(text,bytes,"INVALID %u\r\n",id);
    return snprintf(text,bytes,"SPACE %u %llu %llu %llu %llu %llu\r\n",id,
        (unsigned long long)part.StartingOffset.QuadPart,(unsigned long long)part.PartitionLength.QuadPart,
        unit,(unsigned long long)size.TotalAllocationUnits.QuadPart*unit,
        (unsigned long long)size.AvailableAllocationUnits.QuadPart*unit);
}
int main(void) {
    char text[1024]="XWN-CAPACITY-333\r\n";size_t used=strlen(text);DWORD written=0;
    XVideoSetMode(640,480,32,REFRESH_DEFAULT);debugPrint("Reading E/F capacity; C untouched.\n");
    const char *paths[]={"\\Device\\Harddisk0\\Partition1","\\Device\\Harddisk0\\Partition6"};
    const unsigned ids[]={1,6};
    for(unsigned i=0;i<2;i++){
        int n=query(paths[i],ids[i],text+used,sizeof(text)-used);
        if(n<0||(size_t)n>=sizeof(text)-used){debugPrint("Report bounds failure\n");Sleep(3000);XReboot();return 1;}
        used+=(size_t)n;
    }
    const char end[]="COMPLETE 333\r\n";
    if(used+sizeof(end)>sizeof(text)){Sleep(3000);XReboot();return 1;}
    memcpy(text+used,end,sizeof(end)-1);used+=sizeof(end)-1;
    ANSI_STRING reportName; OBJECT_ATTRIBUTES reportAttrs; IO_STATUS_BLOCK createIo={0};
    HANDLE f=NULL;
    RtlInitAnsiString(&reportName,"\\Device\\Harddisk0\\Partition1\\Applications\\XWNCapacity333\\capacity.txt");
    InitializeObjectAttributes(&reportAttrs,&reportName,OBJ_CASE_INSENSITIVE,NULL,NULL);
    NTSTATUS createStatus=NtCreateFile(&f,GENERIC_WRITE|SYNCHRONIZE,&reportAttrs,&createIo,NULL,
        FILE_ATTRIBUTE_NORMAL,0,FILE_CREATE,FILE_NON_DIRECTORY_FILE|FILE_SYNCHRONOUS_IO_NONALERT);
    int ok=NT_SUCCESS(createStatus);
    if(ok){IO_STATUS_BLOCK io;ok=WriteFile(f,text,(DWORD)used,&written,NULL)&&written==used;
        ok=NT_SUCCESS(NtFlushBuffersFile(f,&io))&&ok;CloseHandle(f);}
    debugPrint("Capacity report %s\n",ok?"saved":"refused");Sleep(3000);XReboot();return ok?0:1;
}
