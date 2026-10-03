/* SPDX-License-Identifier: MIT
 * App-local inventory for native Windows bring-up. No PCI configuration writes,
 * ATA commands, EEPROM access or Windows handoff. nxdk initializes the display.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include "pci-policy.h"

static HANDLE log_file = INVALID_HANDLE_VALUE;
static unsigned device_count;
static int log_ok = 1;

static void report(const char *format, ...)
{
    char text[512]; DWORD written; va_list ap;
    va_start(ap, format); int count = vsnprintf(text, sizeof(text), format, ap); va_end(ap);
    if (count < 0 || count >= (int)sizeof(text)) { log_ok = 0; return; }
    if (log_file != INVALID_HANDLE_VALUE &&
        (!WriteFile(log_file, text, count, &written, NULL) || written != (DWORD)count)) log_ok = 0;
    OutputDebugStringA(text);
}

static unsigned char port_read(unsigned short port)
{
    unsigned char value;
    __asm__ volatile ("inb %1,%0" : "=a"(value) : "Nd"(port));
    return value;
}

static int checkpoint(void)
{
    if (log_file != INVALID_HANDLE_VALUE) {
        IO_STATUS_BLOCK io;
        if ((LONG)NtFlushBuffersFile(log_file,&io)<0) log_ok=0;
    }
    return log_ok;
}

static void pci_inventory(void)
{
    for (unsigned i=0; i<sizeof(pci_targets)/sizeof(pci_targets[0]); ++i) {
        unsigned bus=pci_targets[i].bus, dev=pci_targets[i].dev, fn=pci_targets[i].fn;
        unsigned slot=dev | (fn<<5); uint32_t cfg[16]={0};
        if (!pci_target_allowed(bus,dev,fn)) {
            report("POLICY REJECT %02x:%02x.%u\r\n",bus,dev,fn); continue;
        }
        debugPrint("PCI %02x:%02x.%u ...\n",bus,dev,fn);
        report("BEGIN PCI %02x:%02x.%u offset=00 length=40\r\n",bus,dev,fn);
        if (!checkpoint()) { debugPrint("Log flush failed; scan stopped.\n"); return; }
        HalReadWritePCISpace(bus,slot,0,cfg,sizeof(cfg),FALSE);
        report("END PCI %02x:%02x.%u\r\n",bus,dev,fn);
        if ((cfg[0]&0xffff)==0xffff || (cfg[0]&0xffff)==0) { checkpoint(); continue; }
        const unsigned char *bytes=(const unsigned char *)cfg;
        ++device_count;
        report("PCI %02x:%02x.%u vendor=%04x device=%04x class=%06x rev=%02x header=%02x command=%04x irq=%u pin=%u\r\n",
            bus,dev,fn,cfg[0]&0xffff,cfg[0]>>16,cfg[2]>>8,bytes[8],bytes[14],cfg[1]&0xffff,bytes[60],bytes[61]);
        for (unsigned offset=0; offset<16; offset+=4)
            report("  cfg%02x: %08lx %08lx %08lx %08lx\r\n",offset*4,
                (unsigned long)cfg[offset],(unsigned long)cfg[offset+1],
                (unsigned long)cfg[offset+2],(unsigned long)cfg[offset+3]);
        if (bus==0 && dev==1 && fn==0) {
            uint32_t routing=0;
            report("BEGIN LPC routing offset=6c length=4\r\n");
            if (!checkpoint()) return;
            HalReadWritePCISpace(bus,slot,0x6c,&routing,sizeof(routing),FALSE);
            report("END LPC routing 6c=%08lx\r\n",(unsigned long)routing);
        }
        if (!checkpoint()) return;
    }
}

int main(void)
{
    MM_STATISTICS before={0},after={0}; PVOID inherited=AvGetSavedDataAddress();
    before.Length=sizeof(before); NTSTATUS before_status=MmQueryStatistics(&before);
    unsigned elcr=port_read(0x4d0) | (port_read(0x4d1)<<8);
    DWORD encoder=XVideoGetEncoderSettings();
    log_file=CreateFileA("D:\\xwn-hardware-v2.txt",GENERIC_WRITE,FILE_SHARE_READ,NULL,
                        CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    DWORD file_error=log_file==INVALID_HANDLE_VALUE ? GetLastError() : 0;
    report("XWN hardware inventory v2 - physical hardware status is supplied by the operator\r\n");
    report("kernel=%u.%u.%u.%u flags=%08lx gpu_rev=%u mcpx_rev=%u\r\n",
        XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe,
        XboxHardwareInfo.Flags,XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision);
    report("memory_status=%08lx physical_pages=%lu available_pages=%lu\r\n",
        (unsigned long)before_status,before.TotalPhysicalPages,before.AvailablePages);
    report("inherited_saved_fb=%p encoder_settings=%08lx elcr=%04x\r\n",inherited,encoder,elcr);
    report("BEGIN video initialization 640x480x32 default refresh\r\n");
    checkpoint();
    if (!XVideoSetMode(640,480,32,REFRESH_DEFAULT)) {
        report("VIDEO initialization failed\r\n"); checkpoint();
        if (log_file!=INVALID_HANDLE_VALUE) CloseHandle(log_file);
        for (;;) Sleep(1000);
    }
    debugPrint("XWN hardware probe v2\nHardware inventory - progress below\n\n");
    report("END video initialization\r\n");
    report("PCI policy: known targets only; never 00:00.1 or 00:00.2; no GPU aliases\r\n");
    checkpoint();
    pci_inventory();
    after.Length=sizeof(after); NTSTATUS after_status=MmQueryStatistics(&after);
    unsigned char *fb=XVideoGetFB(); VIDEO_MODE mode=XVideoGetMode();
    report("probe_video=%dx%dx%d@%d framebuffer=%p physical=%08lx\r\n",mode.width,mode.height,mode.bpp,mode.refresh,fb,(unsigned long)MmGetPhysicalAddress(fb));
    report("after_memory_status=%08lx available_pages=%lu pci_functions=%u\r\n",
        (unsigned long)after_status,after.AvailablePages,device_count);
    report("Inventory ended; log_ok=%d. Display initialized by nxdk.\r\n",log_ok);
    if (log_file!=INVALID_HANDLE_VALUE) {
        IO_STATUS_BLOCK io_status;
        if ((LONG)NtFlushBuffersFile(log_file,&io_status)<0) log_ok=0;
        CloseHandle(log_file);log_file=INVALID_HANDLE_VALUE;
    }
    debugClearScreen();
    debugResetCursor();
    debugPrint("Native Windows hardware inventory v2\n\n");
    debugPrint("Kernel %u.%u.%u.%u\n",XboxKrnlVersion.Major,XboxKrnlVersion.Minor,XboxKrnlVersion.Build,XboxKrnlVersion.Qfe);
    debugPrint("RAM: %lu MiB (%lu physical pages)\n",before.TotalPhysicalPages/256,before.TotalPhysicalPages);
    debugPrint("GPU rev %u / MCPX rev %u / flags %08lx\n",XboxHardwareInfo.GpuRevision,XboxHardwareInfo.McpRevision,XboxHardwareInfo.Flags);
    debugPrint("PIC ELCR %04x / video settings %08lx\n",elcr,encoder);
    debugPrint("PCI functions found: %u\n\n",device_count);
    if (!file_error && log_ok) debugPrint("Saved D:\\xwn-hardware-v2.txt\nBeside this app when launched from HDD.\n");
    else debugPrint("Log unavailable (error %lu / write ok %d).\nRun from a writable app folder on HDD.\n",file_error,log_ok);
    debugPrint("\nNo Windows boot or disk-layout changes.\nReboot to return to your dashboard.\n");
    for (;;) Sleep(1000);
}
