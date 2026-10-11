/* SPDX-License-Identifier: MIT
 * Bounded native XID evidence collection; not an NT5 input driver.
 * Only output is D:\xid.log beside the launched XBE on E:.
 * No rumble, interrupt OUT, Windows startup, registry or driver changes.
 */
#include <hal/debug.h>
#include <hal/video.h>
#include <hal/xbox.h>
#include <windows.h>
#include <xboxkrnl/xboxkrnl.h>
#include <usbh_lib.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

static HANDLE log_file = INVALID_HANDLE_VALUE;
static IFACE_T *target;
static UTR_T *request;
static unsigned char *buffer;
static DWORD log_bytes, reports, failures;
static int found_once, ready;

static int record(const char *fmt, ...)
{
    char text[9000]; DWORD written; va_list args;
    va_start(args, fmt);
    int length = vsnprintf(text, sizeof(text), fmt, args);
    va_end(args);
    if (length < 0 || length >= (int)sizeof(text) ||
        (DWORD)length > 1024*1024 - log_bytes ||
        !WriteFile(log_file, text, length, &written, NULL) || written != (DWORD)length) {
        failures++; return 0;
    }
    log_bytes += written; return 1;
}

static void flush_log(void)
{
    IO_STATUS_BLOCK io;
    if (log_file != INVALID_HANDLE_VALUE && !NT_SUCCESS(NtFlushBuffersFile(log_file, &io))) failures++;
}

static void hex_record(const char *tag, unsigned long ms, int status, const void *data, unsigned long size)
{
    static char hex[8193]; const unsigned char *bytes = data;
    static const char digits[] = "0123456789abcdef";
    if (size > 4096) { failures++; return; }
    for (unsigned long i=0; i<size; i++) { hex[2*i]=digits[bytes[i]>>4]; hex[2*i+1]=digits[bytes[i]&15]; }
    hex[2*size]=0;
    record("%s %lu %d %lu %s\r\n", tag, ms, status, size, hex);
}

/* The patched USB core calls this BEFORE freeing an undrained control UTR.
 * All USB allocations stay alive until the firmware reboot resets the machine.
 * No driver unload or core_deinit is attempted with potentially live DMA.
 */
__attribute__((noreturn)) void xid_guard_reboot(void)
{
    failures++;
    record("GUARD_UNDRAINED %lu\r\n", GetTickCount()); flush_log();
    debugPrint("USB request did not drain. Evidence saved; rebooting.\n");
    XReboot();
    for (;;) Sleep(1000);
}

static void drain(void)
{
    if (request && !request->bIsTransferDone) {
        record("CANCEL %lu %d\r\n", GetTickCount(), usbh_quit_utr(request));
        DWORD started=GetTickCount();
        while (!request->bIsTransferDone && GetTickCount()-started < 1000) Sleep(1);
        if (!request->bIsTransferDone) xid_guard_reboot();
        record("DRAINED %lu %d\r\n", GetTickCount(), request->status);
    }
}

static int probe(IFACE_T *iface)
{
    DESC_IF_T *desc=iface->aif->ifd;
    UDEV_T *device=iface->udev;
    int allowed=device->descriptor.idVendor==0xffff && device->descriptor.idProduct==0xffff;
#ifdef XID_EMULATOR
    allowed |= device->descriptor.idVendor==0x045e && device->descriptor.idProduct==0x0202;
#endif
    if (!allowed || found_once || desc->bInterfaceClass!=0x58 ||
        desc->bInterfaceSubClass!=0x42 || desc->bInterfaceProtocol!=0 ||
        desc->bNumEndpoints!=2 || desc->bAlternateSetting!=0) return USBH_ERR_NOT_MATCHED;
    found_once=1;
    hex_record("DEVICE",GetTickCount(),0,&device->descriptor,sizeof(device->descriptor));
    DESC_CONF_T *config=(DESC_CONF_T *)device->cfd_buff;
    if (config->wTotalLength>4096 || config->wTotalLength<9) return USBH_ERR_DESCRIPTOR;
    hex_record("CONFIG",GetTickCount(),0,config,config->wTotalLength);
    EP_INFO_T *in=NULL;
    for (unsigned i=0;i<2;i++) {
        EP_INFO_T *ep=&iface->aif->ep[i];
        record("ENDPOINT %u %u %u %u\r\n",ep->bEndpointAddress,ep->bmAttributes,ep->wMaxPacketSize,ep->bInterval);
        if ((ep->bmAttributes&3)!=3 || ep->wMaxPacketSize!=32 || ep->bInterval!=4) return USBH_ERR_DESCRIPTOR;
        if (ep->bEndpointAddress&0x80) { if(in) return USBH_ERR_DESCRIPTOR; in=ep; }
        else if(ep->bEndpointAddress!=2) return USBH_ERR_DESCRIPTOR;
    }
    if (!in || (in->bEndpointAddress!=0x81 && in->bEndpointAddress!=0x82)) return USBH_ERR_DESCRIPTOR;
    /* USB DMA buffers use the library's uncached pool, never stack memory. */
    buffer=usbh_alloc_mem(32);
    if (!buffer) return USBH_ERR_MEMORY_OUT;
    memset(buffer,0,32);
    uint32_t transferred=0;
    int status=usbh_ctrl_xfer(device,0xc1,6,0x4200,iface->if_num,16,buffer,&transferred,100);
    hex_record("XID",GetTickCount(),status,buffer,transferred<=16?transferred:0);
    if (status || transferred!=16 || buffer[0]!=16 || buffer[1]!=0x42 ||
        buffer[4]!=1 || buffer[6]<2 || buffer[6]>32) return USBH_ERR_DESCRIPTOR;
    request=alloc_utr(device);
    if (!request) return USBH_ERR_MEMORY_OUT;
    request->ep=in; request->buff=buffer; request->data_len=32;
    request->bIsTransferDone=1;
    target=iface; ready=1;
    record("READY %lu %u %u %u\r\n",GetTickCount(),iface->if_num,device->port_num,in->bEndpointAddress);
    flush_log(); return USBH_OK;
}

static void disconnect(IFACE_T *iface)
{
    if (iface==target) { ready=0; failures++; drain(); target=NULL; }
}

static UDEV_DRV_T driver={probe,disconnect,NULL,NULL};

int main(void)
{
    XVideoSetMode(640,480,32,REFRESH_DEFAULT);
    log_file=CreateFileA("D:\\xid.log",GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(log_file==INVALID_HANDLE_VALUE) { debugPrint("Existing log or unwritable app folder; stopped.\n"); Sleep(2000); XReboot(); return 1; }
#ifdef XID_EMULATOR
    record("XWN_XID_CAPTURE 1 emulator\r\n");
#else
    record("XWN_XID_CAPTURE 1 physical\r\n");
#endif
    debugPrint("XID controller capture\nPlease leave the controller connected.\nDetecting controller...\n");
    usbh_core_init(); usbh_register_driver(&driver);
    DWORD start=GetTickCount();
    while (!found_once && GetTickCount()-start<15000) { usbh_pooling_hubs(); Sleep(10); }
    if (!ready) { failures++; record("NO_READY_DEVICE %lu\r\n",GetTickCount()); }
    else {
        /* Stop topology polling after enumeration. Device/iface objects remain
         * pinned through the session, including a physical unplug. No freeing
         * or reconnection is attempted; failed reads end this single capture. */
        debugPrint("Recording for 45 seconds.\nPress buttons, squeeze triggers and move both sticks.\nThen release everything. The Xbox will restart itself.\n");
        start=GetTickCount();
        while (GetTickCount()-start<45000 && reports<2250 && !failures) {
            request->status=0; request->xfer_len=0; request->bIsTransferDone=0;
            int status=usbh_int_xfer(request);
            if(status) { failures++; record("SUBMIT_FAILED %lu %d\r\n",GetTickCount(),status); break; }
            /* An unchanged controller may NAK. Keep its single request alive
             * until the session deadline rather than treating idle as failure. */
            while(!request->bIsTransferDone && GetTickCount()-start<45000) Sleep(1);
            if(!request->bIsTransferDone) { record("CAPTURE_DEADLINE %lu\r\n",GetTickCount()); drain(); break; }
            if(request->xfer_len>32) { failures++; break; }
            hex_record("INPUT",GetTickCount()-start,request->status,buffer,request->xfer_len);
            reports++;
            if(request->status) { failures++; break; }
            if(reports%50==0) flush_log();
            Sleep(20);
        }
    }
    drain();
    record("CAPTURE_END %lu %lu\r\n",reports,failures); flush_log(); CloseHandle(log_file); log_file=INVALID_HANDLE_VALUE;
    debugPrint("Captured %lu reports; %lu errors. Returning to dashboard.\n",reports,failures);
    /* Keep the USB pool alive. Firmware reboot ends the controller's lifetime. */
    Sleep(1500); XReboot(); for (;;) Sleep(1000);
}
