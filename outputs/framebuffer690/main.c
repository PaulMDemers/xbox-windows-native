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
        snprintf(path, size, "E:\\xwn-video690-%02u.json", i);
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


int main(void)
{
    if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
    DWORD settings=XVideoGetEncoderSettings();
    MM_STATISTICS memory={0};memory.Length=sizeof(memory);
    LONG memory_status=MmQueryStatistics(&memory);
    append("{\n  \"schema\":1,\"tool\":\"xwn-framebuffer690\",\n");
    append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
        XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    append("  \"settings\":%lu,\"memory_status\":%lu,\"pages\":%lu,\n",
        (unsigned long)settings,(unsigned long)memory_status,(unsigned long)memory.TotalPhysicalPages);
    if(checkpoint("before_reads",0)){HalReturnToFirmware(HalRebootRoutine);return 2;}
    ULONG pci[3]={0xffffffff,0xffffffff,0xffffffff};
    const ULONG offsets[]={0,4,0x14};
    for(unsigned i=0;i<3;++i)HalReadWritePCISpace(0,1|(1<<5),offsets[i],&pci[i],4,FALSE);
    append("  \"pci_smbus\":{\"bus\":0,\"device\":1,\"function\":1,\"id\":%lu,\"command_status\":%lu,\"bar1\":%lu},\n",
        (unsigned long)pci[0],(unsigned long)pci[1],(unsigned long)pci[2]);
    const unsigned char addresses[]={0x20,0xa8,0xa8,0xa8,0xa8,0xa8,0xe0};
    const unsigned char regs[]={4,0x58,0x59,0x5a,0x5b,0x96,0};
    append("  \"kernel_byte_reads\":[");
    for(unsigned i=0;i<7;++i){
        ULONG value=0xdeadbeef;LONG st=HalReadSMBusValue(addresses[i],regs[i],FALSE,&value);
        append("%s{\"address8\":%u,\"register\":%u,\"status\":%lu,\"value\":%lu}",
            i?",":"",addresses[i],regs[i],(unsigned long)st,(unsigned long)value);
    }
    append("],\n");
    if(checkpoint("after_reads",0)){HalReturnToFirmware(HalRebootRoutine);return 3;}
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
    struct fb690 layout={(uint32_t)MmGetPhysicalAddress(fb),3686400,(uint32_t)MmQueryAllocationSize(fb),5120,1280,720,32,VIDEOREG(0x600800)};
    int layout_ok=framebuffer_admit690(&layout);
    int contiguous=layout_ok;unsigned checked=0;uint32_t first_bad=0xffffffff;
    /* Validate every page and the last byte through the kernel address service. */
    for(unsigned off=0;layout_ok && off<layout.bytes;off+=4096){
        ULONG_PTR actual=MmGetPhysicalAddress((unsigned char*)fb+off);++checked;
        if(actual!=layout.address+off){contiguous=0;first_bad=off;break;}
    }
    if(layout_ok && MmGetPhysicalAddress((unsigned char*)fb+layout.bytes-1)!=layout.address+layout.bytes-1){contiguous=0;first_bad=layout.bytes-1;}
    int admitted=framebuffer_admit690(&layout)&&contiguous;
    append("  \"framebuffer\":{\"physical\":%lu,\"bytes\":%lu,\"allocation\":%lu,\"scanout\":%lu,\"page_checks\":%u,\"first_bad_offset\":%lu,\"contiguous\":%s,\"admitted\":%s,\"native_reserved_overlap\":%d},\n",
        (unsigned long)layout.address,(unsigned long)layout.bytes,(unsigned long)layout.allocation,(unsigned long)layout.scanout,checked,
        (unsigned long)first_bad,contiguous?"true":"false",admitted?"true":"false",handoff_overlap690(layout.address,layout.bytes));
    int saved=checkpoint("allocation_checked",0);
    if(!admitted || saved){HalReturnToFirmware(HalRebootRoutine);return 6;}
    uint32_t *pixels=fb;
    for(unsigned y=0;y<720;++y)for(unsigned x=0;x<1280;++x)pixels[y*1280+x]=checkpoint_pixel690(x,y);
    XVideoFlushFB();
    if(checkpoint("pattern_submitted",0)){HalReturnToFirmware(HalRebootRoutine);return 7;}
    Sleep(15000);checkpoint("restart_requested",1);HalReturnToFirmware(HalRebootRoutine);return 0;
}
