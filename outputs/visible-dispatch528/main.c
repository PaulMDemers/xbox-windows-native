/* SPDX-License-Identifier: MIT; visible standalone control, not Windows. */
#ifdef XWN_HOST_TEST
#include "host-sdk.h"
#else
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <hal/video.h>
#include <hal/debug.h>
#endif
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include "engine.h"
static HANDLE file=INVALID_HANDLE_VALUE;
static int visible;
static void show(const char *format,...)
{
    if (!visible) return;
    char text[256]; va_list args; va_start(args,format);
    vsnprintf(text,sizeof(text),format,args); va_end(args);
    debugPrint("%s",text);
}
static void band(uint32_t color)
{
    if (!visible) return;
    uint32_t *fb=(uint32_t *)XVideoGetFB();
    for (unsigned i=1280*560;i<1280*720;++i) fb[i]=color;
    XVideoFlushFB();
}
static int prepare_e(void)
{
    const char *target="\\Device\\Harddisk0\\Partition1";
    int mounted=nxIsDriveMounted('E'); show("E alias present: %d\n",mounted);
    if (!mounted) {
        show("Mount standard E: "); int ok=nxMountDrive('E',target);
        DWORD error=ok ? 0 : GetLastError(); show("ok=%d error=%08lx\n",ok,(unsigned long)error);
        if (!ok) return 0;
    }
    ANSI_STRING name,value; OBJECT_ATTRIBUTES attributes; HANDLE link;
    char buffer[128]; ULONG returned=0;
    RtlInitAnsiString(&name,"\\??\\E:");
    InitializeObjectAttributes(&attributes,&name,OBJ_CASE_INSENSITIVE,NULL,NULL);
    show("Open E alias: "); NTSTATUS status=NtOpenSymbolicLinkObject(&link,&attributes);
    show("%08lx\n",(unsigned long)(uint32_t)status);
    if (!NT_SUCCESS(status)) return 0;
    memset(buffer,0,sizeof(buffer));value.Buffer=buffer;value.Length=0;value.MaximumLength=sizeof(buffer);
    show("Query E alias: ");status=NtQuerySymbolicLinkObject(link,&value,&returned);
    show("%08lx len=%u returned=%lu\n",(unsigned long)(uint32_t)status,(unsigned)value.Length,(unsigned long)returned);
    show("Close E alias: ");NTSTATUS closed=NtClose(link);
    show("%08lx\n",(unsigned long)(uint32_t)closed);
    if (NT_SUCCESS(status) && value.Length<=sizeof(buffer)) {
        char safe[129];
        for (unsigned i=0;i<value.Length;++i) safe[i]=(buffer[i]>=32 && buffer[i]<=126) ? buffer[i] : '?';
        safe[value.Length]=0;show("Alias target: %s\n",safe);
    }
    int ok=NT_SUCCESS(status) && NT_SUCCESS(closed) && value.Length==strlen(target) &&
           !memcmp(value.Buffer,target,value.Length);
    show("Exact standard E target accepted: %d\n",ok);return ok;
}
static int open_file(void *ctx,unsigned stage,int writing)
{
    (void)ctx;
    const char *path=stage==1 ? "E:\\Applications\\XWNDispatch528\\begin.bin" :
                              "E:\\Applications\\XWNDispatch528\\entry.bin";
    show("File%u %s: ",stage,writing ? "CREATE_NEW" : "OPEN_EXISTING");
    file=CreateFileA(path,writing ? GENERIC_WRITE : GENERIC_READ,writing ? 0 : FILE_SHARE_READ,NULL,
                    writing ? CREATE_NEW : OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    int ok=file!=INVALID_HANDLE_VALUE;DWORD error=ok ? 0 : GetLastError();
    show("ok=%d error=%08lx\n",ok,(unsigned long)error);return ok;
}
static int write_file(void *ctx,const unsigned char *data,size_t n,size_t *got)
{
    (void)ctx;DWORD count=0;show("Write: ");
    int ok=WriteFile(file,data,(DWORD)n,&count,NULL);DWORD error=ok ? 0 : GetLastError();*got=count;
    show("ok=%d bytes=%lu error=%08lx\n",ok,(unsigned long)count,(unsigned long)error);return ok;
}
static int read_file(void *ctx,unsigned char *data,size_t n,size_t *got)
{
    (void)ctx;DWORD count=0;show("Read: ");
    int ok=ReadFile(file,data,(DWORD)n,&count,NULL);DWORD error=ok ? 0 : GetLastError();*got=count;
    show("ok=%d bytes=%lu error=%08lx\n",ok,(unsigned long)count,(unsigned long)error);return ok;
}
static int flush_file(void *ctx)
{
    (void)ctx;IO_STATUS_BLOCK io;show("Flush: ");NTSTATUS status=NtFlushBuffersFile(file,&io);
    show("%08lx\n",(unsigned long)(uint32_t)status);return NT_SUCCESS(status);
}
static int close_file(void *ctx)
{
    (void)ctx;HANDLE once=file;file=INVALID_HANDLE_VALUE;show("Close file: ");
    int ok=CloseHandle(once);DWORD error=ok ? 0 : GetLastError();
    show("ok=%d error=%08lx\n",ok,(unsigned long)error);return ok;
}
int main(void)
{
    visible=XVideoSetMode(1280,720,32,60);
    VIDEO_MODE vm=XVideoGetMode();
    visible=visible && vm.width==1280 && vm.height==720 && vm.bpp==32 &&
            XVideoGetFB()!=NULL && MmQueryAllocationSize(XVideoGetFB())>=1280*720*4;
    if (visible) debugClearScreen();
    band(0x000060c0);show("XWN 528 STANDALONE DISPATCH CONTROL\nBLUE: runtime entered, before E alias and file operations.\n");
    Sleep(12000);
    int ok=0;
    if (prepare_e()) {
        const uint16_t kernel[4]={XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe};
        show("Kernel: %u.%u.%u.%u\n",kernel[0],kernel[1],kernel[2],kernel[3]);
        const struct io528 io={NULL,open_file,write_file,flush_file,close_file,read_file};
        ok=run528(&io,kernel);
    }
    band(ok ? 0x0000a040 : 0x00c02020);
    show("%s: %s\nReturning to dashboard after 20 seconds; Windows was not started.\n",
         ok ? "GREEN" : "RED",ok ? "Both receipt pipelines completed" : "Alias or file operation refused/failed");
    Sleep(20000);HalReturnToFirmware(HalRebootRoutine);return 0;
}
