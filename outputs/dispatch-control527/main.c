/* SPDX-License-Identifier: MIT
 * Standalone runtime control. No Windows/display/PCI/EEPROM operations.
 */
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <string.h>
#include "engine.h"
static HANDLE file=INVALID_HANDLE_VALUE;
static int prepare_e(void)
{
    const char *target="\\Device\\Harddisk0\\Partition1";
    if (!nxIsDriveMounted('E') && !nxMountDrive('E',target)) return 0;
    ANSI_STRING name,value; OBJECT_ATTRIBUTES attributes; HANDLE link;
    char buffer[128]; ULONG returned=0;
    RtlInitAnsiString(&name,"\\??\\E:");
    InitializeObjectAttributes(&attributes,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
    if (!NT_SUCCESS(NtOpenSymbolicLinkObject(&link,&attributes))) return 0;
    value.Buffer=buffer; value.Length=0; value.MaximumLength=sizeof(buffer);
    NTSTATUS status=NtQuerySymbolicLinkObject(link,&value,&returned);
    NTSTATUS closed=NtClose(link);
    return NT_SUCCESS(status) && NT_SUCCESS(closed) && value.Length==strlen(target) &&
           !memcmp(value.Buffer,target,value.Length);
}
static int open_file(void *ctx,unsigned stage,int writing)
{
    (void)ctx;
    const char *path=stage==1 ? "E:\\Applications\\XWNDispatch527\\begin.bin" :
                              "E:\\Applications\\XWNDispatch527\\entry.bin";
    file=CreateFileA(path,writing ? GENERIC_WRITE : GENERIC_READ,
                    writing ? 0 : FILE_SHARE_READ,NULL,
                    writing ? CREATE_NEW : OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    return file!=INVALID_HANDLE_VALUE;
}
static int write_file(void *ctx,const unsigned char *data,size_t n,size_t *got)
{
    (void)ctx; DWORD count=0;
    int ok=WriteFile(file,data,(DWORD)n,&count,NULL); *got=count; return ok;
}
static int read_file(void *ctx,unsigned char *data,size_t n,size_t *got)
{
    (void)ctx; DWORD count=0;
    int ok=ReadFile(file,data,(DWORD)n,&count,NULL); *got=count; return ok;
}
static int flush_file(void *ctx)
{
    (void)ctx; IO_STATUS_BLOCK io;
    return NT_SUCCESS(NtFlushBuffersFile(file,&io));
}
static int close_file(void *ctx)
{
    (void)ctx; HANDLE once=file; file=INVALID_HANDLE_VALUE;
    return CloseHandle(once);
}
int main(void)
{
    if (prepare_e()) {
        const uint16_t kernel[4]={XboxKrnlVersion.Major,XboxKrnlVersion.Minor,
                                 XboxKrnlVersion.Build,XboxKrnlVersion.Qfe};
        const struct io527 io={NULL,open_file,write_file,flush_file,close_file,read_file};
        (void)run527(&io,kernel);
    }
    Sleep(2000);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
