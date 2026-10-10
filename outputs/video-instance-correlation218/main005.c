/* SPDX-License-Identifier: MIT
 * Query-only stock-kernel diagnostic. No GPU stores, pbkit reset, allocator
 * resize, interrupt acknowledgement, cache-policy change or Windows launch.
 */
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include "correlation.h"

#define ROOT "\\Device\\Harddisk0\\Partition1\\xwninst218d"
#define CPU_BASE 0x83feb000u
#define GPU_BASE 0xfd710000u
/* RAM-only observation when disk reporting fails. [1] stage, [2] Win32
 * error, [3] success flag, [4:5] query, [6] complete, [7] restart marker. */
__declspec(dllexport) volatile uint32_t xwn_instance_progress[10]={0x2180cafeu,0,0,0,0,0,0,0,0,0};
static uint32_t cpu[2][INST_WORDS], gpu[2][INST_WORDS];
/* Absolute native paths require a NULL object root. Preserve raw NT status
 * as well as the Windows error; do not create or alter global drive aliases. */
static HANDLE create_native(const char *name,int directory)
{
    ANSI_STRING path;OBJECT_ATTRIBUTES oa;IO_STATUS_BLOCK io;HANDLE h=NULL;
    RtlInitAnsiString(&path,name);
    InitializeObjectAttributes(&oa,&path,OBJ_CASE_INSENSITIVE,NULL,NULL);
    NTSTATUS status=NtCreateFile(&h,directory?(FILE_LIST_DIRECTORY|SYNCHRONIZE):(GENERIC_WRITE|FILE_READ_ATTRIBUTES|SYNCHRONIZE),
      &oa,&io,NULL,FILE_ATTRIBUTE_NORMAL,FILE_SHARE_READ|FILE_SHARE_WRITE,FILE_CREATE,
      FILE_SYNCHRONOUS_IO_NONALERT|(directory?FILE_DIRECTORY_FILE:FILE_NON_DIRECTORY_FILE));
    xwn_instance_progress[8]=(uint32_t)status;
    if((LONG)status<0 || status==STATUS_PENDING){SetLastError(RtlNtStatusToDosError(status));return INVALID_HANDLE_VALUE;}
    SetLastError(ERROR_SUCCESS);return h;
}
static BOOL create_directory_native(const char *name)
{
    HANDLE h=create_native(name,1);if(h==INVALID_HANDLE_VALUE)return FALSE;
    NTSTATUS status=NtClose(h);xwn_instance_progress[9]=(uint32_t)status;
    if((LONG)status<0){SetLastError(RtlNtStatusToDosError(status));return FALSE;}
    return TRUE;
}
static HANDLE log_file=INVALID_HANDLE_VALUE;
static int log_ok=1;
static void report(const char *format,...)
{
    char text[512]; DWORD written=0; va_list ap;
    va_start(ap,format); int n=vsnprintf(text,sizeof(text),format,ap); va_end(ap);
    if(n<0 || n>=(int)sizeof(text)){log_ok=0;return;}
    if(log_file==INVALID_HANDLE_VALUE || !WriteFile(log_file,text,(DWORD)n,&written,NULL) || written!=(DWORD)n)log_ok=0;
}
static int checkpoint(void)
{
    IO_STATUS_BLOCK io;
    if(log_file==INVALID_HANDLE_VALUE || (LONG)NtFlushBuffersFile(log_file,&io)<0)log_ok=0;
    return log_ok;
}
static int save(const char *name,const void *data,DWORD bytes)
{
    char path[128];DWORD written=0;IO_STATUS_BLOCK io;
    if(snprintf(path,sizeof(path),ROOT "\\%s",name)<0)return 0;
    HANDLE h=create_native(path,0);
    if(h==INVALID_HANDLE_VALUE)return 0;
    int ok=WriteFile(h,data,bytes,&written,NULL) && written==bytes;
    if((LONG)NtFlushBuffersFile(h,&io)<0)ok=0;
    if(!CloseHandle(h))ok=0;
    return ok;
}
static int pages(uint32_t base,uint32_t physical)
{
    for(unsigned offset=0;offset<INST_BYTES;offset+=4096){
        PVOID p=(PVOID)(uintptr_t)(base+offset);
        int valid=MmIsAddressValid(p)!=0;
        uint32_t actual=valid?(uint32_t)MmGetPhysicalAddress(p):0xffffffffu;
        report("PAGE %08lx valid=%u physical=%08lx expected=%08lx\r\n",
          (unsigned long)(base+offset),valid,(unsigned long)actual,(unsigned long)(physical+offset));
        if(!valid || actual!=physical+offset)return 0;
    }
    return 1;
}
int main(void)
{
    int complete=0;MM_STATISTICS stats={0};SIZE_T padding=0;
    /* CREATE_NEW and the unique directory prevent any repeat from overwriting
       a partial or completed observation. Failure returns without GPU reads. */
    xwn_instance_progress[1]=2;
    BOOL made=create_directory_native(ROOT);
    xwn_instance_progress[2]=made?0:GetLastError();xwn_instance_progress[3]=made;
    if(!made)goto restart;
    xwn_instance_progress[1]=4;
    log_file=create_native(ROOT "\\report.txt",0);
    xwn_instance_progress[2]=log_file==INVALID_HANDLE_VALUE?GetLastError():0;
    xwn_instance_progress[3]=log_file!=INVALID_HANDLE_VALUE;
    if(log_file==INVALID_HANDLE_VALUE)goto restart;
    xwn_instance_progress[1]=5;
    report("XWN INSTANCE218 QUERY_ONLY\r\n");
    report("KERNEL %u %u %u %u GPU_REV %u MCPX_REV %u FLAGS %08lx\r\n",
      XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
      XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision,(unsigned long)XboxHardwareInfo.Flags);
    stats.Length=sizeof(stats);NTSTATUS ms=MmQueryStatistics(&stats);
    report("MEMORY %08lx PAGES %lu AVAILABLE %lu\r\n",(unsigned long)ms,stats.TotalPhysicalPages,stats.AvailablePages);
    if((LONG)ms<0 || stats.TotalPhysicalPages!=16384 || XboxKrnlVersion.Major!=1 || XboxKrnlVersion.Minor!=0){
        report("PROFILE_REJECT\r\n");goto finish;
    }
    xwn_instance_progress[1]=6;
    PVOID end=MmClaimGpuInstanceMemory((SIZE_T)0xffffffffu,&padding);
    xwn_instance_progress[4]=(uint32_t)(uintptr_t)end;xwn_instance_progress[5]=padding;
    report("QUERY end=%08lx padding=%08lx reference_window_bytes=%u\r\n",
      (unsigned long)(uintptr_t)end,(unsigned long)padding,INST_BYTES);
    if((uintptr_t)end!=0x83ff0000u || padding!=0x10000u){report("QUERY_REJECT\r\n");goto finish;}
    xwn_instance_progress[1]=7;
    if(!pages(CPU_BASE,0x03feb000u) || !pages(GPU_BASE,GPU_BASE)){report("PAGE_REJECT\r\n");goto finish;}
    report("BEGIN_CAPTURE cpu=%08lx gpu=%08lx bytes=%u passes=2 no_cache_flush=1\r\n",
      (unsigned long)CPU_BASE,(unsigned long)GPU_BASE,INST_BYTES);
    if(!checkpoint())goto finish;
    xwn_instance_progress[1]=8;
    for(unsigned pass=0;pass<2;pass++){
        const volatile uint32_t *c=(const volatile uint32_t *)(uintptr_t)CPU_BASE;
        const volatile uint32_t *g=(const volatile uint32_t *)(uintptr_t)GPU_BASE;
        for(unsigned i=0;i<INST_WORDS;i++)cpu[pass][i]=c[i];
        for(unsigned i=0;i<INST_WORDS;i++)gpu[pass][i]=g[i];
        if(pass==0)Sleep(20);
    }
    report("END_CAPTURE\r\n");
    xwn_instance_progress[1]=9;
    if(!save("cpu0.bin",cpu[0],INST_BYTES) || !save("gpu0.bin",gpu[0],INST_BYTES) ||
       !save("cpu1.bin",cpu[1],INST_BYTES) || !save("gpu1.bin",gpu[1],INST_BYTES)){
        report("RAW_SAVE_FAILED\r\n");goto finish;
    }
    INST_RESULT r=inst_compare(cpu[0],cpu[1],gpu[0],gpu[1]);
    report("RESULT cpu_stable=%u gpu_stable=%u nonzero_words=%u distinct_blocks=%u forward_mismatches=%u reverse16_mismatches=%u correlation=%u\r\n",
      r.cpu_stable,r.gpu_stable,r.nonzero_words,r.distinct_blocks,r.forward_mismatches,r.reverse16_mismatches,r.correlation);
    report("LIMITS correlation_is_not_causal_alias_or_nt5_ownership no_gpu_writes no_resize no_windows_launch\r\n");
    complete=1;xwn_instance_progress[1]=10;
finish:
    xwn_instance_progress[6]=complete;
    report("COMPLETE %u LOG_OK %u STOCK_RESTART_REQUEST\r\n",complete,log_ok);
    checkpoint();CloseHandle(log_file);log_file=INVALID_HANDLE_VALUE;
restart:
    xwn_instance_progress[7]=0x52455354u;
    Sleep(2000);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
