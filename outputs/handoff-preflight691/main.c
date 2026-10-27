/* SPDX-License-Identifier: MIT
 * Kernel-owned framebuffer and read-only configuration reference. No native handoff.
 * Kernel display calls are not bounded by this application. Watched test only.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <nxdk/mount.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "layout.h"
#include "plan.h"

static char report[32768], verify[32768];
static size_t used;
static int overflow;

/* DVD launches mount D only. Never replace an existing drive mapping: verify
 * the native target, and refuse any mapping other than standard dashboard E. */
static int prepare_e(void)
{
    const char *target = "\\Device\\Harddisk0\\Partition1";
    if (!nxIsDriveMounted('E') && !nxMountDrive('E', target)) return 0;
    ANSI_STRING name, value;
    OBJECT_ATTRIBUTES attributes;
    HANDLE handle;
    char buffer[128];
    RtlInitAnsiString(&name, "\\??\\E:");
    InitializeObjectAttributes(&attributes, &name, OBJ_CASE_INSENSITIVE, NULL, NULL);
    if (!NT_SUCCESS(NtOpenSymbolicLinkObject(&handle, &attributes))) return 0;
    value.Buffer = buffer; value.Length = 0; value.MaximumLength = sizeof(buffer);
    ULONG returned = 0;
    NTSTATUS status = NtQuerySymbolicLinkObject(handle, &value, &returned);
    NtClose(handle);
    return NT_SUCCESS(status) && value.Length == strlen(target) &&
           !memcmp(value.Buffer, target, value.Length);
}

static void append(const char *fmt, ...)
{
    if (overflow) return;
    va_list args;
    va_start(args, fmt);
    int n = vsnprintf(report + used, sizeof(report) - used, fmt, args);
    va_end(args);
    if (n < 0 || (size_t)n >= sizeof(report) - used) { overflow = 1; return; }
    used += (size_t)n;
}

static int save_report(char *path, size_t size)
{
    HANDLE file = INVALID_HANDLE_VALUE;
    for (unsigned i = 0; i < 100; ++i) {
        snprintf(path, size, "E:\\xwn-handoff691-%02u.json", i);
        file = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
        if (file != INVALID_HANDLE_VALUE) break;
        if (GetLastError() != ERROR_FILE_EXISTS && GetLastError() != ERROR_ALREADY_EXISTS) return 1;
    }
    if (file == INVALID_HANDLE_VALUE) return 2;
    DWORD written = 0;
    IO_STATUS_BLOCK io;
    int ok = WriteFile(file, report, (DWORD)used, &written, NULL) && written == used;
    if ((LONG)NtFlushBuffersFile(file, &io) < 0) ok = 0;
    if (!CloseHandle(file)) ok = 0;
    if (!ok) return 3;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 4;
    DWORD got = 0;
    ok = ReadFile(file, verify, sizeof(verify), &got, NULL) && got == used && !memcmp(report, verify, used);
    if (!CloseHandle(file)) ok = 0;
    return ok ? 0 : 5;
}


static int geometry(const char *stage)
{
    static const unsigned offsets[] = {
        0x600800, 0x680800, 0x680804, 0x68080c, 0x680810, 0x680818,
        0x680820, 0x680824, 0x68082c, 0x680830, 0x680838,
        0x680630, 0x68084c, 0x680880, 0x6808c4
    };
    static const unsigned char indices[] = {0x13, 0x19, 0x28};
    unsigned char original = VIDEOREG8(0x6013d4), crtc[3];
    for (unsigned i = 0; i < 3; ++i) {
        VIDEOREG8(0x6013d4) = indices[i];
        crtc[i] = VIDEOREG8(0x6013d5);
    }
    VIDEOREG8(0x6013d4) = original;
    append("  \"%s\":{\"crtc13_19_28\":[%u,%u,%u],\"pitch_bytes\":%u,\"registers\":[",
           stage, crtc[0], crtc[1], crtc[2], 8 * (((crtc[1] & 0xe0) << 3) | crtc[0]));
    for (unsigned i = 0; i < sizeof(offsets)/sizeof(offsets[0]); ++i)
        append("%s[%u,%lu]", i ? "," : "", offsets[i], (unsigned long)VIDEOREG(offsets[i]));
    append("]},\n");
    return VIDEOREG(0x680838) == 1279 && VIDEOREG(0x680818) == 719 &&
           8 * (((crtc[1] & 0xe0) << 3) | crtc[0]) == 5120 && (crtc[2] & 15) == 3;
}

static int checkpoint(const char *phase, int complete)
{
    char path[64];
    size_t saved_used = used;
    append("  \"phase\":\"%s\",\"complete\":%s\n}\n", phase, complete ? "true" : "false");
    int rc = overflow ? 6 : save_report(path, sizeof(path));
    used = saved_used;
    if (!rc && !strcmp(phase, "before_kernel_mode"))
        append("  \"start_record\":\"%s\",\n", path + 3); /* E-root basename, no JSON escapes. */
    return rc;
}


/* Query only the extent whose allocation metadata and range have passed. */
static int contiguous691(void *v,uint32_t p,uint32_t n){
 for(uint32_t off=0;off<n;off+=4096)if(MmGetPhysicalAddress((char*)v+off)!=p+off)return 0;
 return MmGetPhysicalAddress((char*)v+n-1)==p+n-1;
}
static int allocation_probe691(uint32_t fb,uint32_t fb_bytes){
 struct plan691 p={0};p.framebuffer=fb;p.framebuffer_size=fb_bytes;
 void *source=NULL,*stub=NULL,*alias=NULL;SIZE_T region=4096;int copied=0;
 LONG free_status=0;int alias_created=0;
 if(checkpoint("handoff_before_allocations",0))return 0;
 source=MmAllocateContiguousMemoryEx(0x100000,0x200000,0x1ffffff,0,PAGE_READWRITE);
 if(source){
  p.source=MmGetPhysicalAddress(source);p.source_size=0x100000;p.source_allocation=MmQueryAllocationSize(source);
  if(p.source_allocation>=p.source_size && p.source>=0x200000 && p.source<=0x1f00000 && !(p.source&4095))p.source_contiguous=contiguous691(source,p.source,p.source_size);
 }
 /* Match legacy allocation requests, but refuse null and bad metadata. */
 if(p.source_contiguous)stub=MmAllocateContiguousMemoryEx(4096,0x1000000,0x2000000,16,PAGE_READWRITE);
 if(stub){
  p.stub=MmGetPhysicalAddress(stub);p.stub_size=4096;p.stub_allocation=MmQueryAllocationSize(stub);
  if(p.stub_allocation>=4096 && p.stub>=0x1000000 && p.stub<=0x1fff000 && !(p.stub&4095))p.stub_contiguous=contiguous691(stub,p.stub,4096);
 }
 p.status=0xffffffff;
 if(p.stub_contiguous){
  p.requested=p.stub;alias=(void*)p.requested;
  p.status=NtAllocateVirtualMemory(&alias,0,&region,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
  alias_created=!(p.status&0x80000000);p.returned=(uint32_t)alias;p.region_size=region;
  /* Only query this exact, successful one-page allocation. Changed bases/sizes
   * are still reported and released, but never copied into or queried here. */
  if(alias_created && p.returned==p.requested && region==4096){
   p.alias_physical=MmGetPhysicalAddress(alias);
   p.alias_last=MmGetPhysicalAddress((char*)alias+4095);
  }
 }
 uint32_t refusal=admit691(&p);
 append("  \"handoff_allocations\":{\"source_virtual\":%lu,\"source_physical\":%lu,\"source_allocation\":%lu,\"source_contiguous\":%lu,\"stub_virtual\":%lu,\"stub_physical\":%lu,\"stub_allocation\":%lu,\"stub_contiguous\":%lu,\"virtual_status\":%lu,\"requested\":%lu,\"returned\":%lu,\"region_size\":%lu,\"alias_physical\":%lu,\"alias_last\":%lu,\"refusal_bits\":%lu},\n",
  (unsigned long)source,(unsigned long)p.source,(unsigned long)p.source_allocation,(unsigned long)p.source_contiguous,
  (unsigned long)stub,(unsigned long)p.stub,(unsigned long)p.stub_allocation,(unsigned long)p.stub_contiguous,
  (unsigned long)p.status,(unsigned long)p.requested,(unsigned long)p.returned,(unsigned long)p.region_size,
  (unsigned long)p.alias_physical,(unsigned long)p.alias_last,(unsigned long)refusal);
 if(!checkpoint("handoff_after_allocations",0) && !refusal){
  unsigned char *s=source,*a=alias,*b=stub;
  for(unsigned i=0;i<1024;++i)s[i]=(unsigned char)(i*37+11);
  memset(a,0x5a,4096);memset(b,0x5a,4096);
  memcpy(a,s,1024);memcpy(b,s,1024);copied=!memcmp(a,s,1024)&&!memcmp(b,s,1024);
  for(unsigned i=1024;i<4096;++i)if(a[i]!=0x5a || b[i]!=0x5a)copied=0;
 }
 if(alias_created){SIZE_T zero=0;free_status=NtFreeVirtualMemory(&alias,&zero,MEM_RELEASE);}
 if(stub)MmFreeContiguousMemory(stub);
 if(source)MmFreeContiguousMemory(source);
 append("  \"handoff_cleanup\":{\"copied_and_guards_matched\":%s,\"alias_created\":%s,\"alias_free_status\":%lu,\"source_freed\":%s,\"stub_freed\":%s,\"native_transition\":false},\n",
  copied?"true":"false",alias_created?"true":"false",(unsigned long)free_status,source?"true":"false",stub?"true":"false");
 int saved=checkpoint("handoff_cleaned",0);
 return !refusal && copied && free_status>=0 && !saved;
}

int main(void)
{
    if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
    DWORD settings=XVideoGetEncoderSettings();
    MM_STATISTICS memory={0};memory.Length=sizeof(memory);
    LONG memory_status=MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-handoff-preflight691\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
        XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
        (unsigned long)settings,(unsigned long)memory_status,(unsigned long)memory.TotalPhysicalPages);
    if(checkpoint("start",0)){HalReturnToFirmware(HalRebootRoutine);return 2;}
    unsigned standard=settings&VIDEO_STANDARD_MASK;
    int eligible=(settings&VIDEO_ADAPTER_MASK)==AV_PACK_HDTV && (settings&VIDEO_MODE_720P) &&
        (standard==0x100 || standard==0x200) && !memory_status && memory.TotalPhysicalPages==16384;
    append("  \"eligible_720p\":%s,\n",eligible?"true":"false");
    if(!eligible){checkpoint("configuration_refused",0);HalReturnToFirmware(HalRebootRoutine);return 4;}
    if(checkpoint("before_kernel_mode",0)){HalReturnToFirmware(HalRebootRoutine);return 4;}
    BOOL applied=XVideoSetMode(1280,720,32,60);VIDEO_MODE mode=XVideoGetMode();
    append("  \"mode_return\":%s,\"sdk_mode\":[%d,%d,%d,%d],\n",applied?"true":"false",mode.width,mode.height,mode.bpp,mode.refresh);
    int geom=geometry("geometry");void *fb=XVideoGetFB();
    if(!applied || !geom || mode.width!=1280 || mode.height!=720 || mode.bpp!=32 || mode.refresh!=60 || !fb){
        checkpoint("mode_refused",0);HalReturnToFirmware(HalRebootRoutine);return 5;
    }
    struct fb691 layout={(uint32_t)MmGetPhysicalAddress(fb),3686400,(uint32_t)MmQueryAllocationSize(fb),5120,1280,720,32,VIDEOREG(0x600800)};
    int layout_ok=framebuffer_admit691(&layout);
    int contiguous=layout_ok;unsigned checked=0;uint32_t first_bad=0xffffffff;
    /* Validate every page and the last byte through the kernel address service. */
    for(unsigned off=0;layout_ok && off<layout.bytes;off+=4096){
        ULONG_PTR actual=MmGetPhysicalAddress((unsigned char*)fb+off);++checked;
        if(actual!=layout.address+off){contiguous=0;first_bad=off;break;}
    }
    if(layout_ok && MmGetPhysicalAddress((unsigned char*)fb+layout.bytes-1)!=layout.address+layout.bytes-1){contiguous=0;first_bad=layout.bytes-1;}
    int admitted=framebuffer_admit691(&layout)&&contiguous;
    append("  \"framebuffer\":{\"physical\":%lu,\"bytes\":%lu,\"allocation\":%lu,\"scanout\":%lu,\"page_checks\":%u,\"first_bad_offset\":%lu,\"contiguous\":%s,\"admitted\":%s,\"native_reserved_overlap\":%d},\n",
        (unsigned long)layout.address,(unsigned long)layout.bytes,(unsigned long)layout.allocation,(unsigned long)layout.scanout,checked,
        (unsigned long)first_bad,contiguous?"true":"false",admitted?"true":"false",handoff_overlap691(layout.address,layout.bytes));
    int saved=checkpoint("allocation_checked",0);
    if(!admitted || saved){HalReturnToFirmware(HalRebootRoutine);return 6;}
    int probe_ok=allocation_probe691(layout.address,layout.bytes);
    append("  \"preflight_passed\":%s,\n",probe_ok?"true":"false");
    uint32_t *pixels=fb;
    for(unsigned y=0;y<720;++y)for(unsigned x=0;x<1280;++x)pixels[y*1280+x]=checkpoint_pixel691(x,y);
    for(unsigned y=8;y<80;++y)for(unsigned x=8;x<1272;++x)pixels[y*1280+x]=probe_ok?0x00ff00:0xff0000;
    XVideoFlushFB();
    if(checkpoint("pattern_submitted",0)){HalReturnToFirmware(HalRebootRoutine);return 7;}
    Sleep(15000);checkpoint("restart_requested",1);HalReturnToFirmware(HalRebootRoutine);return 0;
}
