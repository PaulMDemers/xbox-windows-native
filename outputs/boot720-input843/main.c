/* SPDX-License-Identifier: MIT
 * Normalized720p Windows843 handoff; checked RAM-copy bridge. Fixed720p retained-mode Windows boot.
 * Kernel APIs unbounded. No kernel call or automatic return after native entry.
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
#include "page.h"
#include "embed.h"

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
        snprintf(path, size, "E:\\xwn-boot843-%02u.json", i);
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
        0x680630, 0x68084c, 0x680880, 0x6808c4,
        0x600804, 0x680508, 0x68050c, 0x100200
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


/* Kernel-owned context sampling only. PCI reads use the kernel's serialized API;
 * no direct CF8 writes and no native transition. CRTC/SQ indices are restored. */
static int context829(void)
{
 static const unsigned cfg[][3]={{1,0,0},{1,0,4},{1,0,0x10},
  {0,33,0},{0,33,4},{0,33,0x14},{0,1,0},{0,1,4},{0,1,0x10},{0,1,0x84}};
 ULONG pci[10];
 append("  \"pci_kernel_reads\":[");
 for(unsigned i=0;i<10;++i){ULONG value=0xffffffff;
  HalReadWritePCISpace(cfg[i][0],cfg[i][1],cfg[i][2],&value,4,FALSE);pci[i]=value;
  append("%s[%u,%u,%u,%lu]",i?",":"",cfg[i][0],cfg[i][1],cfg[i][2],(unsigned long)value);
 }
 append("],\n");
 static const unsigned char fields[]={0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,
  0x14,0x15,0x16,0x17,0x18,0x19,0x1a,0x1b,0x1f,0x21,0x22,0x25,0x28,0x2d,0x33,0x39,0x44};
 unsigned char index=VIDEOREG8(0x6013d4),seq=VIDEOREG8(0xc03c4),values[sizeof(fields)],sq[5];
 for(unsigned i=0;i<sizeof(fields);++i){VIDEOREG8(0x6013d4)=fields[i];values[i]=VIDEOREG8(0x6013d5);}
 VIDEOREG8(0x6013d4)=index;
 for(unsigned i=0;i<5;++i){VIDEOREG8(0xc03c4)=i;sq[i]=VIDEOREG8(0xc03c5);}
 VIDEOREG8(0xc03c4)=seq;
 int restored=VIDEOREG8(0x6013d4)==index && VIDEOREG8(0xc03c4)==seq;
 append("  \"crtc_kernel_reads\":[");
 for(unsigned i=0;i<sizeof(fields);++i)append("%s[%u,%u]",i?",":"",fields[i],values[i]);
 append("],\n  \"sequencer_kernel_reads\":[%u,%u,%u,%u,%u],\n",sq[0],sq[1],sq[2],sq[3],sq[4]);
 append("  \"selectors_restored\":%s,\"native_transition\":false,\"native_video_programming\":false,\n",restored?"true":"false");
 uint32_t cr0,cr3,cr4,flags;uint16_t cs,ds,ss;
 __asm__ volatile("mov %%cr0,%0":"=r"(cr0));
 __asm__ volatile("mov %%cr3,%0":"=r"(cr3));
 __asm__ volatile("mov %%cr4,%0":"=r"(cr4));
 __asm__ volatile("pushfl;popl %0":"=r"(flags)::"memory");
 __asm__ volatile("mov %%cs,%0":"=r"(cs));
 __asm__ volatile("mov %%ds,%0":"=r"(ds));
 __asm__ volatile("mov %%ss,%0":"=r"(ss));
 append("  \"pre_file_write_cpu\":[%lu,%lu,%lu,%lu,%u,%u,%u],\n",(unsigned long)flags,(unsigned long)cr0,(unsigned long)cr3,(unsigned long)cr4,cs,ds,ss);
 int saved=checkpoint("kernel_context_captured",0);
 int baseline=pci[0]==0x02a010de && (pci[1]&2) && (pci[2]&0xfffffff7)==0xfd000000 &&
  pci[3]==0x01b410de && (pci[4]&1) && pci[5]==0xc001 && pci[6]==0x01b210de &&
  (pci[7]&1) && pci[8]==0 && pci[9]==0x8001;
 unsigned char by_index[256]={0};
 for(unsigned i=0;i<sizeof(fields);++i)by_index[fields[i]]=values[i];
 baseline=baseline && !(by_index[0x11]&0x80) && (by_index[0x21]&0xfa)==0xfa &&
  by_index[0x44]==0 && !(by_index[9]&0x80) && by_index[0x39]==0xff &&
  VIDEOREG(0x680508)==0x3c20d && VIDEOREG(0x68050c)==0x100a0400 &&
  VIDEOREG(0x680880)==0x21101100 && VIDEOREG(0x100200)==0x3070003 && VIDEOREG(0x600804)==3;
 return saved || !restored || !baseline;
}

static struct {void *source,*stub,*reservation;uint32_t target,fb;} armed829;
static void release829(void)
{
 if(armed829.reservation){void *v=armed829.reservation;SIZE_T n=0;LONG rc=NtFreeVirtualMemory(&v,&n,MEM_RELEASE);append("  \"release_status\":%lu,\n",(unsigned long)rc);}
 if(armed829.stub)MmFreeContiguousMemory(armed829.stub);
 if(armed829.source)MmFreeContiguousMemory(armed829.source);
 memset(&armed829,0,sizeof(armed829));
}
static int cpu829(uint32_t v[6])
{
 uint16_t cs,ds,ss;uint32_t a=1,b,c,d;
 __asm__ volatile("pushfl;popl %0":"=r"(v[0])::"memory");
 __asm__ volatile("mov %%cr0,%0":"=r"(v[1]));
 __asm__ volatile("mov %%cr3,%0":"=r"(v[2]));
 __asm__ volatile("mov %%cr4,%0":"=r"(v[3]));
 __asm__ volatile("mov %%cs,%0":"=r"(cs));
 __asm__ volatile("mov %%ds,%0":"=r"(ds));
 __asm__ volatile("mov %%ss,%0":"=r"(ss));
 __asm__ volatile("cpuid":"+a"(a),"=b"(b),"=c"(c),"=d"(d));
 v[4]=cs|((uint32_t)ds<<16);v[5]=ss|(((d>>25)&1)<<16);
 return (v[1]&0x80000001)==0x80000001 && !(v[3]&0x20) && cs==8 && ds==16 && ss==16 && (d&(1<<25)) && (d&16);
}
static int contiguous829(void *v,uint32_t p,uint32_t n)
{
 for(uint32_t off=0;off<n;off+=4096)if(MmGetPhysicalAddress((char*)v+off)!=p+off)return 0;
 return MmGetPhysicalAddress((char*)v+n-1)==p+n-1;
}
static int allocation_probe829(uint32_t fb,uint32_t fb_bytes,uint32_t fb_allocation)
{
 struct plan705 p={0};p.framebuffer=fb;p.framebuffer_size=fb_bytes;p.framebuffer_allocation=fb_allocation;
 void *source=NULL,*stub=NULL,*alias=NULL;SIZE_T region=40960;int copied=0,alias_created=0;
 LONG free_status=0;
 if(checkpoint("before_allocations",0))return 0;
 source=MmAllocateContiguousMemoryEx(0x100000,0x200000,0x1ffffff,0,PAGE_READWRITE);
 if(source){
  p.source=MmGetPhysicalAddress(source);p.source_size=0x100000;p.source_allocation=MmQueryAllocationSize(source);
  if(p.source_allocation>=p.source_size && p.source>=0x200000 && p.source<=0x1f00000 && !(p.source&4095))p.source_contiguous=contiguous829(source,p.source,p.source_size);
 }
 if(p.source_contiguous)stub=MmAllocateContiguousMemoryEx(40960,0x1000000,0x1ffffff,16,PAGE_READWRITE);
 if(stub){
  p.stub=MmGetPhysicalAddress(stub);p.stub_size=40960;p.stub_allocation=MmQueryAllocationSize(stub);
  if(p.stub_allocation>=40960 && p.stub>=0x1000000 && p.stub<=0x1ff6000 && !(p.stub&4095))p.stub_contiguous=contiguous829(stub,p.stub,40960);
 }
 p.status=0xffffffff;
 if(p.stub_contiguous){
  p.requested=p.stub;alias=(void*)p.requested;
  p.status=NtAllocateVirtualMemory(&alias,0,&region,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
  alias_created=!(p.status&0x80000000);p.returned=(uint32_t)alias;p.region_size=region;
  if(alias_created && reservation_contains705(p.requested,p.returned,region)){
   for(unsigned i=0;i<10;++i){p.alias[i]=MmGetPhysicalAddress((void*)(p.requested+4096*i));p.alias_last[i]=MmGetPhysicalAddress((void*)(p.requested+4096*i+4095));}
  }
 }
 uint32_t refusal=admit705(&p);
 append("  \"allocation_plan_words\":[");
 uint32_t words[35];_Static_assert(sizeof(p)==sizeof(words),"plan schema");memcpy(words,&p,sizeof(words));
 for(unsigned i=0;i<sizeof(p)/sizeof(uint32_t);++i)append("%s%lu",i?",":"",(unsigned long)words[i]);
 append("],\n  \"allocation_refusal_bits\":%lu,\n",(unsigned long)refusal);
 if(!checkpoint("after_allocations",0) && !refusal){
  copied=page829(source,bridge_image,bridge_meta,p.stub,fb,p.source+0x10000,sizeof(firmware_image),firmware_sum);
  if(copied){memcpy((char*)source+0x10000,firmware_image,sizeof(firmware_image));copied=!memcmp((char*)source+0x10000,firmware_image,sizeof(firmware_image));}
  if(copied){memcpy((void*)p.requested,source,40960);memcpy(stub,source,40960);
   copied=!memcmp((void*)p.requested,source,40960)&&!memcmp(stub,source,40960);}
 }
 if(copied){
  armed829.source=source;armed829.stub=stub;armed829.reservation=alias;armed829.target=p.requested;armed829.fb=fb;
  append("  \"page_copies_verified\":true,\n");
  if(!checkpoint("native_page_ready",0))return 1;
  release829();return 0;
 }
 if(alias_created){SIZE_T zero=0;free_status=NtFreeVirtualMemory(&alias,&zero,MEM_RELEASE);}
 if(stub)MmFreeContiguousMemory(stub);
 if(source)MmFreeContiguousMemory(source);
 append("  \"cleanup\":{\"copies_verified\":%s,\"bytes\":40960,\"alias_created\":%s,\"alias_free_status\":%lu,\"source_freed\":%s,\"stub_freed\":%s,\"native_transition\":false},\n",
  copied?"true":"false",alias_created?"true":"false",(unsigned long)free_status,source?"true":"false",stub?"true":"false");
 int saved=checkpoint("allocations_released",0);
 return !refusal && copied && free_status>=0 && !saved;
}

int main(void)
{
    if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
    DWORD settings=XVideoGetEncoderSettings();
    MM_STATISTICS memory={0};memory.Length=sizeof(memory);
    LONG memory_status=MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-fixed720-843\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
        XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
        (unsigned long)settings,(unsigned long)memory_status,(unsigned long)memory.TotalPhysicalPages);
    if(checkpoint("start",0)){HalReturnToFirmware(HalRebootRoutine);return 2;}
    ULONGLONG frequency=KeQueryPerformanceFrequency();
    append("  \"kernel_qpc_frequency\":%lu,\n", (unsigned long)frequency);
    if(frequency!=3375000){
        checkpoint("clock_reference_refused",0);HalReturnToFirmware(HalRebootRoutine);return 4;
    }
    unsigned standard=settings&VIDEO_STANDARD_MASK;
    int eligible=(settings&VIDEO_ADAPTER_MASK)==AV_PACK_HDTV && (settings&VIDEO_MODE_720P) && (settings&VIDEO_MODE_480P) &&
        (standard==0x100 || standard==0x200) && !memory_status && memory.TotalPhysicalPages==16384 && XboxHardwareInfo.GpuRevision==0xd3 && XboxHardwareInfo.McpRevision==0xd5;
    append("  \"eligible_720p\":%s,\n",eligible?"true":"false");
    if(!eligible){checkpoint("configuration_refused",0);HalReturnToFirmware(HalRebootRoutine);return 4;}
    if(checkpoint("before_kernel_mode",0)){HalReturnToFirmware(HalRebootRoutine);return 4;}
    BOOL applied=XVideoSetMode(1280,720,32,60);VIDEO_MODE mode=XVideoGetMode();
    append("  \"mode_return\":%s,\"sdk_mode\":[%d,%d,%d,%d],\n",applied?"true":"false",mode.width,mode.height,mode.bpp,mode.refresh);
    int geom=geometry("geometry");void *fb=XVideoGetFB();
    unsigned char saved_index=VIDEOREG8(0x6013d4);
    VIDEOREG8(0x6013d4)=0x39;unsigned interlace=VIDEOREG8(0x6013d5);
    VIDEOREG8(0x6013d4)=saved_index;
    append("  \"kernel_crtc39\":%u,\n",interlace);
    if(!applied || !geom || mode.width!=1280 || mode.height!=720 || mode.bpp!=32 || mode.refresh!=60 || !fb){
        checkpoint("mode_refused",0);HalReturnToFirmware(HalRebootRoutine);return 5;
    }
    struct fb701 layout={(uint32_t)MmGetPhysicalAddress(fb),3686400,(uint32_t)MmQueryAllocationSize(fb),5120,1280,720,32,VIDEOREG(0x600800)};
    int layout_ok=framebuffer_admit701(&layout);
    int contiguous=layout_ok;unsigned checked=0;uint32_t first_bad=0xffffffff;
    /* Validate every page and the last byte through the kernel address service. */
    for(unsigned off=0;layout_ok && off<layout.bytes;off+=4096){
        ULONG_PTR actual=MmGetPhysicalAddress((unsigned char*)fb+off);++checked;
        if(actual!=layout.address+off){contiguous=0;first_bad=off;break;}
    }
    if(layout_ok && MmGetPhysicalAddress((unsigned char*)fb+layout.bytes-1)!=layout.address+layout.bytes-1){contiguous=0;first_bad=layout.bytes-1;}
    int admitted=framebuffer_admit701(&layout)&&contiguous;
    append("  \"framebuffer\":{\"physical\":%lu,\"bytes\":%lu,\"allocation\":%lu,\"scanout\":%lu,\"page_checks\":%u,\"first_bad_offset\":%lu,\"contiguous\":%s,\"admitted\":%s,\"native_reserved_overlap\":%d},\n",
        (unsigned long)layout.address,(unsigned long)layout.bytes,(unsigned long)layout.allocation,(unsigned long)layout.scanout,checked,
        (unsigned long)first_bad,contiguous?"true":"false",admitted?"true":"false",handoff_overlap701(layout.address,layout.bytes));
    int saved=checkpoint("allocation_checked",0);
    if(!admitted || layout.address<0x2800000 || saved){HalReturnToFirmware(HalRebootRoutine);return 6;}
    int state_saved=context829();
    if(state_saved){HalReturnToFirmware(HalRebootRoutine);return 8;}
    int probe_ok=allocation_probe829(layout.address,layout.bytes,layout.allocation);
    append("  \"preflight_passed\":%s,\n",probe_ok?"true":"false");
    uint32_t *pixels=fb;
    for(unsigned y=0;y<720;++y)for(unsigned x=0;x<1280;++x)pixels[y*1280+x]=checkpoint_pixel701(x,y);
    for(unsigned y=8;y<80;++y)for(unsigned x=8;x<1272;++x)pixels[y*1280+x]=probe_ok?0x2080ff:0xff0000;
    XVideoFlushFB();
    if(checkpoint("pattern_submitted",0)){release829();HalReturnToFirmware(HalRebootRoutine);return 7;}
    if(probe_ok){
     Sleep(5000);uint32_t before[6],final[6];int cpu_ok=cpu829(before);
     append("  \"pre_arm_cpu\":[%lu,%lu,%lu,%lu,%lu,%lu],\n",(unsigned long)before[0],(unsigned long)before[1],(unsigned long)before[2],(unsigned long)before[3],(unsigned long)before[4],(unsigned long)before[5]);
     if(cpu_ok && !checkpoint("handoff_armed",0) && VIDEOREG(0x600800)==armed829.fb &&
        !memcmp((void*)armed829.target,armed829.source,40960) && !memcmp(armed829.stub,armed829.source,40960) && !memcmp((char*)armed829.source+0x10000,firmware_image,sizeof(firmware_image)) && cpu829(final)){
      /* Final context is RAM-only in checksum-excluded scratch8e8..900.
       * No API after this point. Source copy remains the original template. */
      memcpy((char*)armed829.stub+0x8e8,final,sizeof(final));
      memcpy((char*)armed829.target+0x8e8,final,sizeof(final));
      __asm__ volatile("sfence; jmp *%0"::"r"(armed829.target):"memory");
      __builtin_unreachable();
     }
     release829();checkpoint("handoff_refused",0);
    }
    Sleep(10000);checkpoint("restart_requested",1);HalReturnToFirmware(HalRebootRoutine);return 0;
}
