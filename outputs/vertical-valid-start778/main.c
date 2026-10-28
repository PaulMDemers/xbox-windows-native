/* SPDX-License-Identifier: MIT
 * Kernel778 seven horizontal timing writes, recover before output-enable; no native handoff.
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
#include "probe.h"

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
        snprintf(path, size, "E:\\xwn-mode778-%02u.json", i);
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
static int context778(void)
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

int main(void)
{
    if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
    DWORD settings=XVideoGetEncoderSettings();
    MM_STATISTICS memory={0};memory.Length=sizeof(memory);
    LONG memory_status=MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-native-mode778\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
        XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
        (unsigned long)settings,(unsigned long)memory_status,(unsigned long)memory.TotalPhysicalPages);
    if(checkpoint("start",0)){HalReturnToFirmware(HalRebootRoutine);return 2;}
    ULONGLONG frequency=KeQueryPerformanceFrequency();
    append("  \"kernel_qpc_frequency\":%lu,\"kernel_qpc_frequency_high\":%lu,\n", (unsigned long)frequency, (unsigned long)(frequency>>32));
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
    if(!admitted || saved){HalReturnToFirmware(HalRebootRoutine);return 6;}
    int state_saved=context778();
    if(state_saved){HalReturnToFirmware(HalRebootRoutine);return 8;}
    if(checkpoint("vertical_valid_start_control_armed",0)){HalReturnToFirmware(HalRebootRoutine);return 9;}
    struct result778 result;probe778(&result);
    append("  \"kernel_sample_words\":[");
    uint32_t words[340];_Static_assert(sizeof(result)==sizeof(words),"result words");memcpy(words,&result,sizeof(words));
    for(unsigned i=0;i<340;++i)append("%s%lu",i?",":"",(unsigned long)words[i]);
    append("],\n  \"native_handoff_performed\":false,\n");
    int recorded=checkpoint("vertical_valid_start_control_returned",0);
    /* Never draw or flush a diagnostic picture after failed timing restoration.
     * Reports are saved even with output blank, then firmware recovery is requested. */
    if(result.h_cleanup_mask || result.c4_cleanup_mask || result.c0_cleanup_mask || result.c2_cleanup_mask || result.c3_cleanup_mask || result.c5b_cleanup_mask || result.c17_cleanup_mask || result.c1_cleanup_mask || result.c2b_cleanup_mask || result.c17b_cleanup_mask || result.c19b_cleanup_mask || result.c13_cleanup_mask || result.v_cleanup_mask || result.vt_cleanup_mask || result.vc_cleanup_mask || result.vs_cleanup_mask){checkpoint("restart_requested",!recorded);HalReturnToFirmware(HalRebootRoutine);return 10;}
    uint32_t color=recorded?0xff00ff:result.code==0x778?0x00ff00:(result.code==0x7788 || result.code==0x7785 || result.code==0x7789 || result.code==0x778b || result.code==0x778d || result.code==0x778e || result.code==0x77810 || result.code==0x77812 || result.code==0x77814 || result.code==0x77816 || result.code==0x77818 || result.code==0x7781a || result.code==0x7781c || result.code==0x7781e || result.code==0x77820 || result.code==0x77822 || result.code==0x77824 || result.code==0x77826 || result.code==0x77828)?0xff8000:0xff0000;
    uint32_t *pixels=fb;
    for(unsigned y=0;y<720;++y)for(unsigned x=0;x<1280;++x)pixels[y*1280+x]=checkpoint_pixel701(x,y);
    for(unsigned y=8;y<80;++y)for(unsigned x=8;x<1272;++x)pixels[y*1280+x]=color;
    XVideoFlushFB();
    Sleep(15000);checkpoint("restart_requested",!recorded);HalReturnToFirmware(HalRebootRoutine);return 0;
}
