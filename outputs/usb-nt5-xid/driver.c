/* SPDX-License-Identifier: MIT
 * Original NT5 XID transport/HID minidriver. Experimental, see DESIGN.md.
 * All code and state are resident; no pageable completion or worker buffers.
 */
#define _WIN32_WINNT 0x0500
#define NTDDI_VERSION 0x05000000
#include "nt5hid.h"
#include <usbdrivr.h>
#include "xid_hid.h"
#define TAG 0x64695858UL
typedef struct {
    PDEVICE_OBJECT Lower;
    IO_REMOVE_LOCK Remove;
    KMUTEX Gate;
    KSPIN_LOCK CacheLock;
    KEVENT Stop;
    HANDLE Thread;
    USBD_PIPE_HANDLE Pipe;
    BOOLEAN Configured, Started, D0, Gone, Removing, Active, Valid, Fault;
    UCHAR Report[XWN_REPORT_SIZE];
    XWN_HID_ATTRIBUTES Attributes;
    ULONG Samples, Empty, Invalid, Timeouts, Errors;
} DEVICE;
typedef struct { PIO_WORKITEM Work; DEVICE *Device; PIRP Irp; } POWER_WORK;
#define EXT(fdo) ((DEVICE *)((XWN_HID_EXTENSION *)(fdo)->DeviceExtension)->MiniDeviceExtension)
typedef char urb_header_size[(sizeof(struct _URB_HEADER)==16)?1:-1];
typedef char urb_bulk_size[(sizeof(struct _URB_BULK_OR_INTERRUPT_TRANSFER)==72)?1:-1];
static NTSTATUS finish(PIRP irp,NTSTATUS status,ULONG length)
{
    irp->IoStatus.Status=status; irp->IoStatus.Information=length;
    IoCompleteRequest(irp,IO_NO_INCREMENT); return status;
}
static void gate(DEVICE *d) { KeWaitForSingleObject(&d->Gate,Executive,KernelMode,FALSE,NULL); }
static void ungate(DEVICE *d) { KeReleaseMutex(&d->Gate,FALSE); }
static void active(DEVICE *d,BOOLEAN value)
{
    KIRQL irql; KeAcquireSpinLock(&d->CacheLock,&irql);
    d->Active=value; KeReleaseSpinLock(&d->CacheLock,irql);
}
static NTSTATUS NTAPI signal_done(PDEVICE_OBJECT fdo,PIRP irp,PVOID context)
{
    (void)fdo; (void)irp; KeSetEvent((PKEVENT)context,IO_NO_INCREMENT,FALSE);
    return STATUS_MORE_PROCESSING_REQUIRED;
}
/* Completion retains the allocated IRP. Even after timeout, cancel never grants
 * permission to free it: only the completion event does. This also makes the
 * completed-before-IoCancelIrp race safe because the IRP remains allocated. */
static NTSTATUS usb(DEVICE *d,PURB urb,ULONG milliseconds)
{
    KEVENT done; LARGE_INTEGER due; PIRP irp; PIO_STACK_LOCATION next; NTSTATUS status;
    irp=IoAllocateIrp(d->Lower->StackSize,FALSE);
    if(!irp) return STATUS_INSUFFICIENT_RESOURCES;
    KeInitializeEvent(&done,NotificationEvent,FALSE);
    irp->RequestorMode=KernelMode; irp->IoStatus.Status=STATUS_NOT_SUPPORTED;
    next=IoGetNextIrpStackLocation(irp);
    next->MajorFunction=IRP_MJ_INTERNAL_DEVICE_CONTROL;
    next->Parameters.DeviceIoControl.IoControlCode=IOCTL_INTERNAL_USB_SUBMIT_URB;
    next->Parameters.Others.Argument1=urb;
    IoSetCompletionRoutine(irp,signal_done,&done,TRUE,TRUE,TRUE);
    IoCallDriver(d->Lower,irp);
    due.QuadPart=-(LONGLONG)milliseconds*10000;
    status=KeWaitForSingleObject(&done,Executive,KernelMode,FALSE,&due);
    if(status==STATUS_TIMEOUT) {
        IoCancelIrp(irp);
        KeWaitForSingleObject(&done,Executive,KernelMode,FALSE,NULL);
        status=STATUS_IO_TIMEOUT;
    } else {
        status=irp->IoStatus.Status;
        if(NT_SUCCESS(status) && !USBD_SUCCESS(urb->UrbHeader.Status)) status=STATUS_IO_DEVICE_ERROR;
    }
    IoFreeIrp(irp); return status;
}
static NTSTATUS lower_sync(DEVICE *d,PIRP irp,BOOLEAN power)
{
    KEVENT done;
    KeInitializeEvent(&done,NotificationEvent,FALSE);
    IoCopyCurrentIrpStackLocationToNext(irp);
    IoSetCompletionRoutine(irp,signal_done,&done,TRUE,TRUE,TRUE);
    if(power) PoCallDriver(d->Lower,irp); else IoCallDriver(d->Lower,irp);
    /* PnP/power IRPs belong to the caller: do not invent a timeout/free path. */
    KeWaitForSingleObject(&done,Executive,KernelMode,FALSE,NULL);
    return irp->IoStatus.Status;
}
static NTSTATUS NTAPI release_done(PDEVICE_OBJECT fdo,PIRP irp,PVOID context)
{
    DEVICE *d=context; (void)fdo;
    if(irp->PendingReturned) IoMarkIrpPending(irp);
    IoReleaseRemoveLock(&d->Remove,irp); return STATUS_CONTINUE_COMPLETION;
}
static NTSTATUS forward(DEVICE *d,PIRP irp,BOOLEAN power)
{
    IoCopyCurrentIrpStackLocationToNext(irp);
    IoSetCompletionRoutine(irp,release_done,d,TRUE,TRUE,TRUE);
    if(power) { PoStartNextPowerIrp(irp); return PoCallDriver(d->Lower,irp); }
    return IoCallDriver(d->Lower,irp);
}
static NTSTATUS read_sample(DEVICE *d)
{
    URB urb; UCHAR bytes[32],report[XWN_REPORT_SIZE]; xwn_xid_sample sample;
    NTSTATUS status; int decoded; KIRQL irql;
    RtlZeroMemory(&urb,sizeof(urb));
    UsbBuildInterruptOrBulkTransferRequest(&urb,sizeof(struct _URB_BULK_OR_INTERRUPT_TRANSFER),
        d->Pipe,bytes,NULL,sizeof(bytes),USBD_TRANSFER_DIRECTION_IN|USBD_SHORT_TRANSFER_OK,NULL);
    status=usb(d,&urb,100);
    if(status==STATUS_IO_TIMEOUT) { d->Timeouts++; return status; }
    if(!NT_SUCCESS(status)) { d->Errors++; return status; }
    decoded=xwn_xid_decode(bytes,urb.UrbBulkOrInterruptTransfer.TransferBufferLength,&sample);
    if(decoded==XWN_XID_NO_DATA) { d->Empty++; return STATUS_NO_DATA_DETECTED; }
    if(decoded!=XWN_XID_SAMPLE) { d->Invalid++; return STATUS_DATA_ERROR; }
    xwn_xid_to_hid(&sample,report);
    KeAcquireSpinLock(&d->CacheLock,&irql);
    RtlCopyMemory(d->Report,report,sizeof(report)); d->Valid=TRUE; d->Samples++;
    KeReleaseSpinLock(&d->CacheLock,irql); return STATUS_SUCCESS;
}
static VOID NTAPI reader(PVOID context)
{
    DEVICE *d=context; NTSTATUS status; LARGE_INTEGER pause; KIRQL irql;
    pause.QuadPart=-10000;
    while(!KeReadStateEvent(&d->Stop)) {
        status=read_sample(d);
        if(!NT_SUCCESS(status) && status!=STATUS_IO_TIMEOUT &&
           status!=STATUS_NO_DATA_DETECTED && status!=STATUS_DATA_ERROR) {
            KeAcquireSpinLock(&d->CacheLock,&irql); d->Fault=TRUE;
            KeReleaseSpinLock(&d->CacheLock,irql); break;
        }
        /* A broken device producing empty completions must not spin a CPU. */
        KeDelayExecutionThread(KernelMode,FALSE,&pause);
    }
    PsTerminateSystemThread(STATUS_SUCCESS);
}
static void stop_reader(DEVICE *d)
{
    active(d,FALSE);
    if(d->Thread) {
        KeSetEvent(&d->Stop,IO_NO_INCREMENT,FALSE);
        ZwWaitForSingleObject(d->Thread,FALSE,NULL);
        ZwClose(d->Thread); d->Thread=NULL;
    }
}
static NTSTATUS unconfigure(DEVICE *d)
{
    URB urb; NTSTATUS status=STATUS_SUCCESS;
    if(d->Configured && !d->Gone) {
        RtlZeroMemory(&urb,sizeof(urb));
        UsbBuildSelectConfigurationRequest(&urb,sizeof(struct _URB_SELECT_CONFIGURATION),NULL);
        status=usb(d,&urb,2000);
    }
    d->Pipe=NULL; d->Configured=FALSE; return status;
}
static NTSTATUS start_usb(DEVICE *d)
{
    USB_DEVICE_DESCRIPTOR device; UCHAR config[32],xid[16],endpoint;
    URB urb; PURB selection; USBD_INTERFACE_LIST_ENTRY interfaces[2];
    NTSTATUS status; ULONG i; OBJECT_ATTRIBUTES attributes; KIRQL irql;
    RtlZeroMemory(&urb,sizeof(urb)); RtlZeroMemory(&device,sizeof(device));
    UsbBuildGetDescriptorRequest(&urb,sizeof(struct _URB_CONTROL_DESCRIPTOR_REQUEST),
        USB_DEVICE_DESCRIPTOR_TYPE,0,0,&device,NULL,sizeof(device),NULL);
    status=usb(d,&urb,2000);
    if(!NT_SUCCESS(status)) return status;
    if(urb.UrbControlDescriptorRequest.TransferBufferLength!=sizeof(device) ||
       device.bLength!=18 || device.bDescriptorType!=1 || device.bNumConfigurations!=1 ||
       device.idVendor!=0x045e || device.idProduct!=0x0202) return STATUS_DEVICE_CONFIGURATION_ERROR;
    RtlZeroMemory(&urb,sizeof(urb));
    UsbBuildGetDescriptorRequest(&urb,sizeof(struct _URB_CONTROL_DESCRIPTOR_REQUEST),
        USB_CONFIGURATION_DESCRIPTOR_TYPE,0,0,config,NULL,sizeof(config),NULL);
    status=usb(d,&urb,2000);
    if(!NT_SUCCESS(status)) return status;
    if(!xwn_xid_config(config,urb.UrbControlDescriptorRequest.TransferBufferLength,&endpoint))
        return STATUS_DEVICE_CONFIGURATION_ERROR;
    RtlZeroMemory(interfaces,sizeof(interfaces));
    interfaces[0].InterfaceDescriptor=(PUSB_INTERFACE_DESCRIPTOR)(config+9);
    selection=USBD_CreateConfigurationRequestEx((PUSB_CONFIGURATION_DESCRIPTOR)config,interfaces);
    if(!selection) return STATUS_INSUFFICIENT_RESOURCES;
    status=usb(d,selection,2000);
    d->Configured=selection->UrbSelectConfiguration.ConfigurationHandle!=NULL;
    if(NT_SUCCESS(status)) {
        PUSBD_INTERFACE_INFORMATION info=interfaces[0].Interface;
        if(!info || info->NumberOfPipes!=2) status=STATUS_DEVICE_CONFIGURATION_ERROR;
        else for(i=0;i<info->NumberOfPipes;i++) {
            if(info->Pipes[i].EndpointAddress==endpoint && info->Pipes[i].PipeType==UsbdPipeTypeInterrupt &&
               info->Pipes[i].MaximumPacketSize==32) d->Pipe=info->Pipes[i].PipeHandle;
        }
        if(!d->Pipe) status=STATUS_DEVICE_CONFIGURATION_ERROR;
    }
    ExFreePool(selection);
    if(!NT_SUCCESS(status)) goto failed;
    RtlZeroMemory(&urb,sizeof(urb));
    UsbBuildVendorRequest(&urb,URB_FUNCTION_VENDOR_INTERFACE,sizeof(struct _URB_CONTROL_VENDOR_OR_CLASS_REQUEST),
        USBD_TRANSFER_DIRECTION_IN|USBD_SHORT_TRANSFER_OK,0,6,0x4200,0,xid,NULL,sizeof(xid),NULL);
    status=usb(d,&urb,2000);
    if(!NT_SUCCESS(status)) goto failed;
    if(!xwn_xid_descriptor(xid,urb.UrbControlVendorClassRequest.TransferBufferLength)) {
        status=STATUS_DEVICE_CONFIGURATION_ERROR; goto failed;
    }
    KeAcquireSpinLock(&d->CacheLock,&irql); d->Valid=FALSE; d->Fault=FALSE;
    d->Attributes.Size=sizeof(d->Attributes); d->Attributes.VendorID=device.idVendor;
    d->Attributes.ProductID=device.idProduct; d->Attributes.VersionNumber=device.bcdDevice;
    KeReleaseSpinLock(&d->CacheLock,irql);
    /* A finite number of real attempts; never manufacture the first HID state. */
    for(i=0;i<50;i++) {
        status=read_sample(d);
        if(status==STATUS_SUCCESS) break;
        if(status!=STATUS_IO_TIMEOUT && status!=STATUS_NO_DATA_DETECTED && status!=STATUS_DATA_ERROR) break;
    }
    if(status!=STATUS_SUCCESS) goto failed;
    KeClearEvent(&d->Stop);
    InitializeObjectAttributes(&attributes,NULL,OBJ_KERNEL_HANDLE,NULL,NULL);
    status=PsCreateSystemThread(&d->Thread,THREAD_ALL_ACCESS,&attributes,NULL,NULL,reader,d);
    if(!NT_SUCCESS(status)) goto failed;
    active(d,TRUE); return STATUS_SUCCESS;
failed:
    unconfigure(d); return status;
}
static NTSTATUS NTAPI internal(PDEVICE_OBJECT fdo,PIRP irp)
{
    DEVICE *d=EXT(fdo); PIO_STACK_LOCATION s=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS status; ULONG size=0; UCHAR hid[9]; KIRQL irql;
    status=IoAcquireRemoveLock(&d->Remove,irp);
    if(!NT_SUCCESS(status)) return finish(irp,status,0);
    status=STATUS_NOT_SUPPORTED;
    if(irp->Cancel) status=STATUS_CANCELLED;
    else if(!irp->UserBuffer) status=STATUS_INVALID_PARAMETER;
    else switch(s->Parameters.DeviceIoControl.IoControlCode) {
    case XWN_HID_DESCRIPTOR:
        hid[0]=9;hid[1]=0x21;hid[2]=0x10;hid[3]=1;hid[4]=0;hid[5]=1;hid[6]=0x22;
        hid[7]=(UCHAR)xwn_report_descriptor_size;hid[8]=(UCHAR)(xwn_report_descriptor_size>>8);
        size=sizeof(hid);
        if(s->Parameters.DeviceIoControl.OutputBufferLength<size) status=STATUS_BUFFER_TOO_SMALL;
        else { RtlCopyMemory(irp->UserBuffer,hid,size);status=STATUS_SUCCESS; }
        break;
    case XWN_HID_REPORT_DESCRIPTOR:
        size=xwn_report_descriptor_size;
        if(s->Parameters.DeviceIoControl.OutputBufferLength<size) status=STATUS_BUFFER_TOO_SMALL;
        else { RtlCopyMemory(irp->UserBuffer,xwn_report_descriptor,size);status=STATUS_SUCCESS; }
        break;
    case XWN_HID_ATTRIBUTES_CTL:
        size=sizeof(d->Attributes);
        if(s->Parameters.DeviceIoControl.OutputBufferLength<size) status=STATUS_BUFFER_TOO_SMALL;
        else {
            KeAcquireSpinLock(&d->CacheLock,&irql);
            RtlCopyMemory(irp->UserBuffer,&d->Attributes,size);
            KeReleaseSpinLock(&d->CacheLock,irql);status=STATUS_SUCCESS;
        }
        break;
    case XWN_HID_READ:
        size=XWN_REPORT_SIZE;
        if(s->Parameters.DeviceIoControl.OutputBufferLength<size) status=STATUS_BUFFER_TOO_SMALL;
        else {
            KeAcquireSpinLock(&d->CacheLock,&irql);
            if(!d->Active || !d->Valid || d->Fault) status=STATUS_DEVICE_NOT_READY;
            else { RtlCopyMemory(irp->UserBuffer,d->Report,size);status=STATUS_SUCCESS; }
            KeReleaseSpinLock(&d->CacheLock,irql);
        }
        break;
    }
    if(!NT_SUCCESS(status)) size=0;
    IoReleaseRemoveLock(&d->Remove,irp); return finish(irp,status,size);
}
static NTSTATUS NTAPI pnp(PDEVICE_OBJECT fdo,PIRP irp)
{
    DEVICE *d=EXT(fdo); UCHAR minor=IoGetCurrentIrpStackLocation(irp)->MinorFunction;
    NTSTATUS status=IoAcquireRemoveLock(&d->Remove,irp);
    if(!NT_SUCCESS(status)) return finish(irp,status,0);
    gate(d);
    if(d->Removing) { ungate(d);IoReleaseRemoveLock(&d->Remove,irp);return finish(irp,STATUS_DELETE_PENDING,0); }
    switch(minor) {
    case IRP_MN_START_DEVICE:
        status=lower_sync(d,irp,FALSE);
        if(NT_SUCCESS(status) && !d->Started && !d->Gone) {
            status=start_usb(d); if(NT_SUCCESS(status)) { d->Started=TRUE;d->D0=TRUE; }
        }
        break;
    case IRP_MN_QUERY_STOP_DEVICE:
    case IRP_MN_QUERY_REMOVE_DEVICE:
        if(d->Started) status=STATUS_DEVICE_BUSY;
        else { ungate(d);return forward(d,irp,FALSE); }
        break;
    case IRP_MN_STOP_DEVICE:
        stop_reader(d);unconfigure(d);d->Started=FALSE;d->D0=FALSE;
        irp->IoStatus.Status=STATUS_SUCCESS;ungate(d);return forward(d,irp,FALSE);
    case IRP_MN_SURPRISE_REMOVAL:
        d->Gone=TRUE;stop_reader(d);unconfigure(d);d->Started=FALSE;d->D0=FALSE;
        irp->IoStatus.Status=STATUS_SUCCESS;ungate(d);return forward(d,irp,FALSE);
    case IRP_MN_REMOVE_DEVICE:
        d->Removing=TRUE;stop_reader(d);unconfigure(d);d->Started=FALSE;d->D0=FALSE;
        ungate(d);IoReleaseRemoveLockAndWait(&d->Remove,irp);
        irp->IoStatus.Status=STATUS_SUCCESS;IoSkipCurrentIrpStackLocation(irp);
        return IoCallDriver(d->Lower,irp); /* HIDCLASS owns detach/delete. */
    default: ungate(d);return forward(d,irp,FALSE);
    }
    ungate(d);IoReleaseRemoveLock(&d->Remove,irp);return finish(irp,status,0);
}
static VOID NTAPI power_worker(PDEVICE_OBJECT fdo,PVOID context)
{
    POWER_WORK *w=context; DEVICE *d=w->Device; PIRP irp=w->Irp;
    DEVICE_POWER_STATE target=IoGetCurrentIrpStackLocation(irp)->Parameters.Power.State.DeviceState;
    NTSTATUS status; BOOLEAN was_d0; (void)fdo;
    gate(d);
    was_d0=d->D0;
    if(d->Removing || d->Gone) status=STATUS_DELETE_PENDING;
    else {
        if(target!=PowerDeviceD0 && d->D0) { stop_reader(d);unconfigure(d);d->D0=FALSE; }
        status=lower_sync(d,irp,TRUE);
        if(!NT_SUCCESS(status) && target!=PowerDeviceD0 && was_d0 && d->Started) {
            /* A failed transition leaves the bus in D0: restore its reader. */
            if(NT_SUCCESS(start_usb(d))) d->D0=TRUE;
        }
        if(NT_SUCCESS(status) && target==PowerDeviceD0 && d->Started && !d->D0) {
            status=start_usb(d);if(NT_SUCCESS(status)) d->D0=TRUE;
        }
    }
    ungate(d);PoStartNextPowerIrp(irp);
    IoFreeWorkItem(w->Work);ExFreePool(w);
    IoReleaseRemoveLock(&d->Remove,irp);finish(irp,status,0);
}
static NTSTATUS NTAPI power(PDEVICE_OBJECT fdo,PIRP irp)
{
    DEVICE *d=EXT(fdo); PIO_STACK_LOCATION s=IoGetCurrentIrpStackLocation(irp);
    POWER_WORK *w; NTSTATUS status=IoAcquireRemoveLock(&d->Remove,irp);
    if(!NT_SUCCESS(status)) { PoStartNextPowerIrp(irp);return finish(irp,status,0); }
    if(s->MinorFunction!=IRP_MN_SET_POWER || s->Parameters.Power.Type!=DevicePowerState) return forward(d,irp,TRUE);
    w=ExAllocatePoolWithTag(NonPagedPool,sizeof(*w),TAG);
    if(w) {
        w->Work=IoAllocateWorkItem(fdo);
        if(w->Work) {
            w->Device=d;w->Irp=irp;IoMarkIrpPending(irp);
            IoQueueWorkItem(w->Work,power_worker,DelayedWorkQueue,w);return STATUS_PENDING;
        }
        ExFreePool(w);
    }
    PoStartNextPowerIrp(irp);IoReleaseRemoveLock(&d->Remove,irp);
    return finish(irp,STATUS_INSUFFICIENT_RESOURCES,0);
}
static NTSTATUS NTAPI pass(PDEVICE_OBJECT fdo,PIRP irp)
{
    DEVICE *d=EXT(fdo); NTSTATUS status=IoAcquireRemoveLock(&d->Remove,irp);
    if(!NT_SUCCESS(status)) return finish(irp,status,0);
    return forward(d,irp,FALSE);
}
static NTSTATUS NTAPI stub(PDEVICE_OBJECT fdo,PIRP irp)
{ (void)fdo;return finish(irp,STATUS_NOT_SUPPORTED,0); }
static NTSTATUS NTAPI add(PDRIVER_OBJECT driver,PDEVICE_OBJECT fdo)
{
    DEVICE *d=EXT(fdo);(void)driver;RtlZeroMemory(d,sizeof(*d));
    d->Lower=((XWN_HID_EXTENSION *)fdo->DeviceExtension)->NextDeviceObject;
    IoInitializeRemoveLock(&d->Remove,TAG,0,0);KeInitializeMutex(&d->Gate,0);
    KeInitializeSpinLock(&d->CacheLock);KeInitializeEvent(&d->Stop,NotificationEvent,FALSE);
    fdo->Flags|=DO_POWER_PAGABLE;return STATUS_SUCCESS;
}
static VOID NTAPI unload(PDRIVER_OBJECT driver) { (void)driver; }
NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT driver,PUNICODE_STRING path)
{
    XWN_HID_REGISTRATION registration;
    driver->MajorFunction[IRP_MJ_CREATE]=stub;driver->MajorFunction[IRP_MJ_CLOSE]=stub;
    driver->MajorFunction[IRP_MJ_INTERNAL_DEVICE_CONTROL]=internal;
    driver->MajorFunction[IRP_MJ_SYSTEM_CONTROL]=pass;
    driver->MajorFunction[IRP_MJ_PNP]=pnp;driver->MajorFunction[IRP_MJ_POWER]=power;
    driver->DriverExtension->AddDevice=add;driver->DriverUnload=unload;
    RtlZeroMemory(&registration,sizeof(registration));registration.Revision=1;
    registration.DriverObject=driver;registration.RegistryPath=path;
    registration.DeviceExtensionSize=sizeof(DEVICE);registration.DevicesArePolled=TRUE;
    return HidRegisterMinidriver(&registration);
}
