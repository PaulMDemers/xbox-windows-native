/* SPDX-License-Identifier: MIT
 * Kernel720p -> exact720x480p ->720p snapshots722. No native handoff.
 * Diagnostic GPU data registers are read-only; mode API owns programming.
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
#include "capture.h"

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
        snprintf(path, size, "E:\\xwn-mode722-%02u.json", i);
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

static void begin_record(unsigned stage,const char *phase,uint32_t settings)
{
 used=0;overflow=0;
 append("{\n  \"tool\":\"xwn-kernel-mode722\",\"schema\":1,\"stage\":%u,\"phase\":\"%s\",\n",stage,phase);
 append("  \"kernel\":[%u,%u,%u,%u],\"gpu_revision\":%u,\"mcp_revision\":%u,\"settings\":%lu,\n",
  XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
  XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision,(unsigned long)settings);
 append("  \"native_handoff\":false,\"diagnostic_gpu_data_writes\":false,\n");
}
static int finish_record(int complete)
{
 char path[64];append("  \"complete\":%s\n}\n",complete?"true":"false");
 return overflow?6:save_report(path,sizeof(path));
}
static void dump_capture(const struct capture722 *c)
{
 append("  \"flags\":[%lu,%lu,%lu],\"control_registers\":[%lu,%lu,%lu],\n",
  (unsigned long)c->flags_entry,(unsigned long)c->flags_critical,(unsigned long)c->flags_restored,
  (unsigned long)c->cr0,(unsigned long)c->cr3,(unsigned long)c->cr4);
 append("  \"selectors\":[%lu,%lu,%lu],\"selectors_after\":[%lu,%lu,%lu],\"selectors_restored\":%s,\n",
  (unsigned long)c->selectors[0],(unsigned long)c->selectors[1],(unsigned long)c->selectors[2],
  (unsigned long)c->selectors_after[0],(unsigned long)c->selectors_after[1],(unsigned long)c->selectors_after[2],
  c->selectors_restored?"true":"false");
 append("  \"mmio\":[");
 for(unsigned i=0;i<MMIO722;++i)append("%s[%lu,%lu]",i?",":"",(unsigned long)mmio722[i],(unsigned long)c->mmio[i]);
 append("],\n  \"crtc\":[");
 for(unsigned i=0;i<CRTC722;++i)append("%s[%u,%lu]",i?",":"",crtc722[i],(unsigned long)c->crtc[i]);
 append("],\n  \"sequencer\":[");
 for(unsigned i=0;i<5;++i)append("%s%lu",i?",":"",(unsigned long)c->seq[i]);
 append("],\n  \"graphics\":[");
 for(unsigned i=0;i<9;++i)append("%s%lu",i?",":"",(unsigned long)c->graphics[i]);
 append("],\n");
}
static uint32_t cr_value(const struct capture722 *c,uint8_t index)
{
 for(unsigned i=0;i<CRTC722;++i)if(crtc722[i]==index)return c->crtc[i];
 return 0xffffffff;
}
static int capture_ok(const struct capture722 *c)
{
 return c->selectors_restored && c->flags_entry==c->flags_restored && !(c->flags_critical&0x200);
}
int main(void)
{
 if(!prepare_e()){HalReturnToFirmware(HalRebootRoutine);return 1;}
 uint32_t settings=XVideoGetEncoderSettings();unsigned standard=settings&VIDEO_STANDARD_MASK;
 MM_STATISTICS memory={0};memory.Length=sizeof(memory);LONG m=MmQueryStatistics(&memory);
 int eligible=!m && memory.TotalPhysicalPages==16384 &&
  XboxHardwareInfo.GpuRevision==0xd3 && XboxHardwareInfo.McpRevision==0xd5 &&
  (settings&VIDEO_ADAPTER_MASK)==AV_PACK_HDTV && (settings&VIDEO_MODE_480P) &&
  (settings&VIDEO_MODE_720P) && (standard==0x100 || standard==0x200);
 begin_record(0,"start",settings);
 append("  \"eligible\":%s,\"memory_status\":%lu,\"pages\":%lu,\n",eligible?"true":"false",(unsigned long)m,(unsigned long)memory.TotalPhysicalPages);
 if(finish_record(0) || !eligible){HalReturnToFirmware(HalRebootRoutine);return 2;}
 const unsigned widths[3]={1280,720,1280},heights[3]={720,480,720};
 const uint32_t colors[3]={0x2080ff,0x00ff00,0x00ffff};
 for(unsigned stage=0;stage<3;++stage){
  unsigned w=widths[stage],h=heights[stage];
  begin_record(stage,"mode_requested",settings);
  append("  \"requested\":[%u,%u,32,60],\n",w,h);
  if(finish_record(0) || XVideoGetEncoderSettings()!=settings){HalReturnToFirmware(HalRebootRoutine);return 3;}
  BOOL applied=XVideoSetMode(w,h,32,60);VIDEO_MODE mode=XVideoGetMode();
  void *fb=XVideoGetFB();struct capture722 c;capture722(&c);
  uint32_t a=fb?(uint32_t)MmGetPhysicalAddress(fb):0;
  uint32_t n=fb?(uint32_t)MmQueryAllocationSize(fb):0;
  uint32_t pitch=(cr_value(&c,0x13)|((cr_value(&c,0x19)&0xe0)<<3)|((cr_value(&c,0x25)&0x20)<<6))<<3;
  int admitted=fb && applied && mode.width==(int)w && mode.height==(int)h && mode.bpp==32 && mode.refresh==60 &&
   layout722(a,n,c.mmio[0],w,h,pitch) && c.mmio[22]+1==h && c.mmio[29]+1==w &&
   (cr_value(&c,0x28)&15)==3 && cr_value(&c,0x39)==255 && capture_ok(&c);
  uint32_t checks=0,bad=0xffffffff;
  for(uint32_t off=0;admitted && off<w*h*4;off+=4096){
   ++checks;if(MmGetPhysicalAddress((char*)fb+off)!=a+off){bad=off;admitted=0;}
  }
  if(admitted && MmGetPhysicalAddress((char*)fb+w*h*4-1)!=a+w*h*4-1){bad=w*h*4-1;admitted=0;}
  begin_record(stage,"mode_captured",settings);
  append("  \"requested\":[%u,%u,32,60],\"applied\":%s,\"sdk_mode\":[%d,%d,%d,%d],\n",w,h,applied?"true":"false",mode.width,mode.height,mode.bpp,mode.refresh);
  append("  \"framebuffer\":{\"address\":%lu,\"allocation\":%lu,\"bytes\":%u,\"pitch\":%lu,\"page_checks\":%lu,\"first_bad\":%lu,\"admitted\":%s},\n",
   (unsigned long)a,(unsigned long)n,w*h*4,(unsigned long)pitch,(unsigned long)checks,(unsigned long)bad,admitted?"true":"false");
  dump_capture(&c);
  if(finish_record(0) || !admitted){HalReturnToFirmware(HalRebootRoutine);return 4;}
  uint32_t *pixels=fb;
  for(unsigned y=0;y<h;++y)for(unsigned x=0;x<w;++x)pixels[y*w+x]=pixel722(x,y,w,h,colors[stage]);
  XVideoFlushFB();Sleep(12000);
  capture722(&c);begin_record(stage,"visible_captured",settings);dump_capture(&c);
  append("  \"pattern_color\":%lu,\"hold_ms\":12000,\"capture_ok\":%s,\n",(unsigned long)colors[stage],capture_ok(&c)?"true":"false");
  if(finish_record(0) || !capture_ok(&c) || XVideoGetEncoderSettings()!=settings){HalReturnToFirmware(HalRebootRoutine);return 5;}
 }
 begin_record(3,"restart_requested",settings);finish_record(1);HalReturnToFirmware(HalRebootRoutine);return 0;
}


