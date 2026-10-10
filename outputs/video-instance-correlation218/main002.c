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

#define ROOT "\\Device\\Harddisk0\\Partition6\\xwninst218a"
#define CPU_BASE 0x83feb000u
#define GPU_BASE 0xfd710000u
static uint32_t cpu[2][INST_WORDS], gpu[2][INST_WORDS];
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
    HANDLE h=CreateFileA(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
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
    if(!CreateDirectoryA(ROOT,NULL))goto restart;
    log_file=CreateFileA(ROOT "\\report.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,
                        CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(log_file==INVALID_HANDLE_VALUE)goto restart;
    report("XWN INSTANCE218 QUERY_ONLY\r\n");
    report("KERNEL %u %u %u %u GPU_REV %u MCPX_REV %u FLAGS %08lx\r\n",
      XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
      XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision,(unsigned long)XboxHardwareInfo.Flags);
    stats.Length=sizeof(stats);NTSTATUS ms=MmQueryStatistics(&stats);
    report("MEMORY %08lx PAGES %lu AVAILABLE %lu\r\n",(unsigned long)ms,stats.TotalPhysicalPages,stats.AvailablePages);
    if((LONG)ms<0 || stats.TotalPhysicalPages!=16384 || XboxKrnlVersion.Major!=1 || XboxKrnlVersion.Minor!=0){
        report("PROFILE_REJECT\r\n");goto finish;
    }
    PVOID end=MmClaimGpuInstanceMemory((SIZE_T)0xffffffffu,&padding);
    report("QUERY end=%08lx padding=%08lx reference_window_bytes=%u\r\n",
      (unsigned long)(uintptr_t)end,(unsigned long)padding,INST_BYTES);
    if((uintptr_t)end!=0x83ff0000u || padding!=0x10000u){report("QUERY_REJECT\r\n");goto finish;}
    if(!pages(CPU_BASE,0x03feb000u) || !pages(GPU_BASE,GPU_BASE)){report("PAGE_REJECT\r\n");goto finish;}
    report("BEGIN_CAPTURE cpu=%08lx gpu=%08lx bytes=%u passes=2 no_cache_flush=1\r\n",
      (unsigned long)CPU_BASE,(unsigned long)GPU_BASE,INST_BYTES);
    if(!checkpoint())goto finish;
    for(unsigned pass=0;pass<2;pass++){
        const volatile uint32_t *c=(const volatile uint32_t *)(uintptr_t)CPU_BASE;
        const volatile uint32_t *g=(const volatile uint32_t *)(uintptr_t)GPU_BASE;
        for(unsigned i=0;i<INST_WORDS;i++)cpu[pass][i]=c[i];
        for(unsigned i=0;i<INST_WORDS;i++)gpu[pass][i]=g[i];
        if(pass==0)Sleep(20);
    }
    report("END_CAPTURE\r\n");
    if(!save("cpu0.bin",cpu[0],INST_BYTES) || !save("gpu0.bin",gpu[0],INST_BYTES) ||
       !save("cpu1.bin",cpu[1],INST_BYTES) || !save("gpu1.bin",gpu[1],INST_BYTES)){
        report("RAW_SAVE_FAILED\r\n");goto finish;
    }
    INST_RESULT r=inst_compare(cpu[0],cpu[1],gpu[0],gpu[1]);
    report("RESULT cpu_stable=%u gpu_stable=%u nonzero_words=%u distinct_blocks=%u forward_mismatches=%u reverse16_mismatches=%u correlation=%u\r\n",
      r.cpu_stable,r.gpu_stable,r.nonzero_words,r.distinct_blocks,r.forward_mismatches,r.reverse16_mismatches,r.correlation);
    report("LIMITS correlation_is_not_causal_alias_or_nt5_ownership no_gpu_writes no_resize no_windows_launch\r\n");
    complete=1;
finish:
    report("COMPLETE %u LOG_OK %u STOCK_RESTART_REQUEST\r\n",complete,log_ok);
    checkpoint();CloseHandle(log_file);log_file=INVALID_HANDLE_VALUE;
restart:
    Sleep(2000);
    HalReturnToFirmware(HalRebootRoutine);
    return 0;
}
