/* SPDX-License-Identifier: MIT
 * NT5 MCPX resource-review derivative; telemetry disabled pending shared ownership.
 * The assigned port resource stays at C000 because the existing HAL owns reboot.
 */
#define _WIN32_WINNT 0x0500
#define NTDDI_VERSION 0x05000000
#include <ntddk.h>
#include "resources.h"
#define TAG 0x37626d53UL
#define IOCTL_TELEMETRY CTL_CODE(FILE_DEVICE_UNKNOWN, 0x807, METHOD_BUFFERED, FILE_READ_ACCESS)
static const GUID TelemetryGuid = {0x4cecfd27,0x4cde,0x4cc9,{0xa2,0x92,0xd5,0xcf,0x42,0x3e,0x57,0x07}};
typedef struct extension {
    PDEVICE_OBJECT lower,self;
    IO_REMOVE_LOCK remove;
    FAST_MUTEX mutex;
    UNICODE_STRING link;
    ULONG port;
    unsigned resource_profile;
    ULONG starts, stops, queries, powers;
    LONG started, powered, shutdown, quarantined;
    LONG query, previous;
    LONG power_previous;
    DEVICE_POWER_STATE power_target;
} extension;
typedef struct request { ULONG version, address, command; } request;
typedef struct response { ULONG version, result, polls, attempts, status, data; } response;
static NTSTATUS finish(PIRP irp, NTSTATUS status, ULONG bytes)
{
    irp->IoStatus.Status=status; irp->IoStatus.Information=bytes;
    IoCompleteRequest(irp,IO_NO_INCREMENT); return status;
}
static NTSTATUS NTAPI release(PDEVICE_OBJECT device,PIRP irp,PVOID context)
{
    extension *e=context; UNREFERENCED_PARAMETER(device);
    if(irp->PendingReturned) IoMarkIrpPending(irp);
    IoReleaseRemoveLock(&e->remove,irp); return STATUS_SUCCESS;
}
static NTSTATUS forward(extension *e,PIRP irp,BOOLEAN power)
{
    IoCopyCurrentIrpStackLocationToNext(irp);
    IoSetCompletionRoutine(irp,release,e,TRUE,TRUE,TRUE);
    if(power) { PoStartNextPowerIrp(irp); return PoCallDriver(e->lower,irp); }
    return IoCallDriver(e->lower,irp);
}
static NTSTATUS NTAPI signal_event(PDEVICE_OBJECT device,PIRP irp,PVOID context)
{
    UNREFERENCED_PARAMETER(device); UNREFERENCED_PARAMETER(irp);
    KeSetEvent(context,IO_NO_INCREMENT,FALSE); return STATUS_MORE_PROCESSING_REQUIRED;
}
static NTSTATUS forward_wait(extension *e,PIRP irp)
{
    KEVENT event; NTSTATUS s;
    KeInitializeEvent(&event,NotificationEvent,FALSE);
    IoCopyCurrentIrpStackLocationToNext(irp);
    IoSetCompletionRoutine(irp,signal_event,&event,TRUE,TRUE,TRUE);
    s=IoCallDriver(e->lower,irp);
    if(s==STATUS_PENDING) KeWaitForSingleObject(&event,Executive,KernelMode,FALSE,NULL);
    return irp->IoStatus.Status;
}
static NTSTATUS NTAPI dispatch(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension; PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS s; ULONG bytes=0;
    if(sp->MajorFunction==IRP_MJ_CLOSE || sp->MajorFunction==IRP_MJ_CLEANUP)
        return finish(irp,STATUS_SUCCESS,0);
    s=IoAcquireRemoveLock(&e->remove,irp);
    if(!NT_SUCCESS(s)) return finish(irp,s,0);
    if(sp->MajorFunction!=IRP_MJ_CREATE && sp->MajorFunction!=IRP_MJ_DEVICE_CONTROL && sp->MajorFunction!=IRP_MJ_SHUTDOWN)
        return forward(e,irp,FALSE);
    if(KeGetCurrentIrql()>APC_LEVEL) { s=STATUS_INVALID_DEVICE_STATE; goto done; }
    ExAcquireFastMutex(&e->mutex);
    if(sp->MajorFunction==IRP_MJ_SHUTDOWN) {
        e->shutdown=1; s=STATUS_SUCCESS;
    } else if(!e->started || !e->powered || e->shutdown || e->quarantined || e->query) {
        s=STATUS_DEVICE_NOT_READY;
    } else if(sp->MajorFunction==IRP_MJ_CREATE) {
        s=sp->FileObject->FileName.Length ? STATUS_OBJECT_NAME_NOT_FOUND : STATUS_SUCCESS;
    } else if(sp->Parameters.DeviceIoControl.IoControlCode==CTL_CODE(FILE_DEVICE_UNKNOWN,0x808,METHOD_BUFFERED,FILE_READ_ACCESS)) {
        ULONG *v=irp->AssociatedIrp.SystemBuffer;
        if(sp->Parameters.DeviceIoControl.InputBufferLength || sp->Parameters.DeviceIoControl.OutputBufferLength<40) s=STATUS_BUFFER_TOO_SMALL;
        else { v[0]=1;v[1]=e->resource_profile;v[2]=e->port;v[3]=e->started;v[4]=e->powered;
               v[5]=e->starts;v[6]=e->stops;v[7]=e->queries;v[8]=e->powers;v[9]=0;
               s=STATUS_SUCCESS;bytes=40; }
    } else if(sp->Parameters.DeviceIoControl.IoControlCode!=IOCTL_TELEMETRY) {
        s=STATUS_INVALID_DEVICE_REQUEST;
    } else if(sp->Parameters.DeviceIoControl.InputBufferLength!=sizeof(request) ||
              sp->Parameters.DeviceIoControl.OutputBufferLength<sizeof(response)) {
        s=STATUS_BUFFER_TOO_SMALL;
    } else {
        /* No SMBus operation until HAL takeover/quarantine is coordinated. */
        s=STATUS_NOT_SUPPORTED;
    }
    ExReleaseFastMutex(&e->mutex);
done:
    IoReleaseRemoveLock(&e->remove,irp); return finish(irp,s,bytes);
}
C_ASSERT(sizeof(CM_PARTIAL_RESOURCE_DESCRIPTOR)==16);
C_ASSERT(FIELD_OFFSET(CM_RESOURCE_LIST,List[0].PartialResourceList.PartialDescriptors)==20);
static NTSTATUS validate_resources(PCM_RESOURCE_LIST list,unsigned profile,ULONG *port)
{
    ULONG count;
    if(!list || list->Count!=1)return STATUS_DEVICE_CONFIGURATION_ERROR;
    count=list->List[0].PartialResourceList.Count;
    if(count>16 || xwn_check_resources((const unsigned char*)list,20+count*16,profile))
        return STATUS_DEVICE_CONFIGURATION_ERROR;
    *port=0xc000;return STATUS_SUCCESS;
}
static NTSTATUS NTAPI pnp(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension; PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS s=IoAcquireRemoveLock(&e->remove,irp);
    if(!NT_SUCCESS(s)) return finish(irp,s,0);
    switch(sp->MinorFunction) {
    case IRP_MN_FILTER_RESOURCE_REQUIREMENTS:
        irp->IoStatus.Status=STATUS_SUCCESS;
        s=forward_wait(e,irp);
        if(NT_SUCCESS(s)) {
            PIO_RESOURCE_REQUIREMENTS_LIST list=(PVOID)irp->IoStatus.Information;
            if(!list || xwn_pin_resources((unsigned char*)list,list->ListSize,&e->resource_profile))
                s=STATUS_DEVICE_CONFIGURATION_ERROR;
        }
        /* Information is the OS-owned requirements pointer, not an I/O length. */
        irp->IoStatus.Status=s; IoReleaseRemoveLock(&e->remove,irp);
        IoCompleteRequest(irp,IO_NO_INCREMENT); return s;
    case IRP_MN_START_DEVICE:
        s=validate_resources(sp->Parameters.StartDevice.AllocatedResources,e->resource_profile,&e->port);
        if(NT_SUCCESS(s)) s=validate_resources(sp->Parameters.StartDevice.AllocatedResourcesTranslated,e->resource_profile,&e->port);
        if(NT_SUCCESS(s)) s=forward_wait(e,irp);
        if(NT_SUCCESS(s)) {
            ExAcquireFastMutex(&e->mutex);
            ++e->starts; e->started=1; e->powered=1; e->shutdown=0; e->quarantined=0; e->query=0;
            ExReleaseFastMutex(&e->mutex);
            s=IoSetDeviceInterfaceState(&e->link,TRUE);
            if(!NT_SUCCESS(s)) { ExAcquireFastMutex(&e->mutex); e->started=0; ExReleaseFastMutex(&e->mutex); }
        }
        IoReleaseRemoveLock(&e->remove,irp); return finish(irp,s,0);
    case IRP_MN_QUERY_STOP_DEVICE:
    case IRP_MN_QUERY_REMOVE_DEVICE:
        ExAcquireFastMutex(&e->mutex); ++e->queries; e->previous=e->query; e->query=sp->MinorFunction; ExReleaseFastMutex(&e->mutex);
        irp->IoStatus.Status=STATUS_SUCCESS;
        s=forward_wait(e,irp);
        if(!NT_SUCCESS(s)) { ExAcquireFastMutex(&e->mutex); e->query=e->previous; ExReleaseFastMutex(&e->mutex); }
        IoReleaseRemoveLock(&e->remove,irp); return finish(irp,s,0);
    case IRP_MN_CANCEL_STOP_DEVICE:
    case IRP_MN_CANCEL_REMOVE_DEVICE:
        irp->IoStatus.Status=STATUS_SUCCESS;
        s=forward_wait(e,irp);
        if(NT_SUCCESS(s)) { ExAcquireFastMutex(&e->mutex); e->query=e->previous; ExReleaseFastMutex(&e->mutex); }
        IoReleaseRemoveLock(&e->remove,irp); return finish(irp,s,0);
    case IRP_MN_STOP_DEVICE:
    case IRP_MN_SURPRISE_REMOVAL:
    case IRP_MN_REMOVE_DEVICE:
        ExAcquireFastMutex(&e->mutex); ++e->stops; e->started=0; ExReleaseFastMutex(&e->mutex);
        IoSetDeviceInterfaceState(&e->link,FALSE);
        if(sp->MinorFunction==IRP_MN_REMOVE_DEVICE) {
            PDEVICE_OBJECT lower=e->lower;
            IoReleaseRemoveLockAndWait(&e->remove,irp);
            IoUnregisterShutdownNotification(device);
            RtlFreeUnicodeString(&e->link);
            irp->IoStatus.Status=STATUS_SUCCESS; IoSkipCurrentIrpStackLocation(irp);
            s=IoCallDriver(lower,irp); IoDetachDevice(lower); IoDeleteDevice(device); return s;
        }
        irp->IoStatus.Status=STATUS_SUCCESS; break;
    default: break;
    }
    return forward(e,irp,FALSE);
}
static NTSTATUS NTAPI power_complete(PDEVICE_OBJECT device,PIRP irp,PVOID context)
{
    extension *e=context; UNREFERENCED_PARAMETER(device);
    if(NT_SUCCESS(irp->IoStatus.Status)) {
        POWER_STATE state; state.DeviceState=e->power_target;
        PoSetPowerState(e->self,DevicePowerState,state);
        InterlockedExchange(&e->powered,e->power_target==PowerDeviceD0);
    } else InterlockedExchange(&e->powered,e->power_previous);
    return release(device,irp,context);
}
static NTSTATUS power_passive(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension; PIO_STACK_LOCATION sp=IoGetCurrentIrpStackLocation(irp);
    if(sp->MinorFunction==IRP_MN_SET_POWER && sp->Parameters.Power.Type==DevicePowerState) {
        /* Called at PASSIVE_LEVEL, including elevated requests queued below. */
        ExAcquireFastMutex(&e->mutex);
        ++e->powers; e->power_previous=InterlockedExchange(&e->powered,0);
        e->power_target=sp->Parameters.Power.State.DeviceState;
        ExReleaseFastMutex(&e->mutex);
        /* NT5 serializes SET_POWER for each device; completion still holds remove. */
        IoCopyCurrentIrpStackLocationToNext(irp); IoSetCompletionRoutine(irp,power_complete,e,TRUE,TRUE,TRUE);
        PoStartNextPowerIrp(irp); return PoCallDriver(e->lower,irp);
    }
    return forward(e,irp,TRUE);
}
typedef struct power_work {
    PIO_WORKITEM work;
    PIRP irp;
} power_work;
static VOID NTAPI power_worker(PDEVICE_OBJECT device,PVOID context)
{
    power_work *w=context; PIRP irp=w->irp;
    IoFreeWorkItem(w->work); ExFreePool(w);
    (void)power_passive(device,irp);
}
static NTSTATUS NTAPI power(PDEVICE_OBJECT device,PIRP irp)
{
    extension *e=device->DeviceExtension; NTSTATUS s=IoAcquireRemoveLock(&e->remove,irp);
    if(!NT_SUCCESS(s)) { PoStartNextPowerIrp(irp); return finish(irp,s,0); }
    if(KeGetCurrentIrql()!=PASSIVE_LEVEL) {
        power_work *w=ExAllocatePoolWithTag(NonPagedPool,sizeof(*w),TAG);
        if(w) {
            w->work=IoAllocateWorkItem(device); w->irp=irp;
            if(w->work) {
                IoMarkIrpPending(irp); IoQueueWorkItem(w->work,power_worker,DelayedWorkQueue,w);
                return STATUS_PENDING;
            }
            ExFreePool(w);
        }
        PoStartNextPowerIrp(irp); IoReleaseRemoveLock(&e->remove,irp);
        return finish(irp,STATUS_INSUFFICIENT_RESOURCES,0);
    }
    return power_passive(device,irp);
}
static NTSTATUS NTAPI add(PDRIVER_OBJECT driver,PDEVICE_OBJECT pdo)
{
    PDEVICE_OBJECT device; extension *e; NTSTATUS s; ULONG bytes; WCHAR ids[512];
    UNICODE_STRING actual,expected;
    s=IoGetDeviceProperty(pdo,DevicePropertyHardwareID,sizeof(ids),ids,&bytes);
    if(!NT_SUCCESS(s) || bytes<sizeof(WCHAR)*2 || bytes>sizeof(ids)) return STATUS_NO_SUCH_DEVICE;
    ids[511]=0; RtlInitUnicodeString(&actual,ids);
    RtlInitUnicodeString(&expected,L"PCI\\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1");
    if(!RtlEqualUnicodeString(&actual,&expected,TRUE)) return STATUS_NO_SUCH_DEVICE;
    s=IoCreateDevice(driver,sizeof(extension),NULL,FILE_DEVICE_UNKNOWN,FILE_DEVICE_SECURE_OPEN,FALSE,&device);
    if(!NT_SUCCESS(s)) return s;
    e=device->DeviceExtension; RtlZeroMemory(e,sizeof(*e)); e->self=device;
    IoInitializeRemoveLock(&e->remove,TAG,0,0); ExInitializeFastMutex(&e->mutex);
    e->lower=IoAttachDeviceToDeviceStack(device,pdo);
    if(!e->lower) { IoDeleteDevice(device); return STATUS_NO_SUCH_DEVICE; }
    s=IoRegisterDeviceInterface(pdo,&TelemetryGuid,NULL,&e->link);
    if(NT_SUCCESS(s)) s=IoRegisterShutdownNotification(device);
    if(!NT_SUCCESS(s)) { if(e->link.Buffer) RtlFreeUnicodeString(&e->link); IoDetachDevice(e->lower); IoDeleteDevice(device); return s; }
    device->Flags |= DO_BUFFERED_IO|DO_POWER_PAGABLE;
    device->Flags &= ~DO_DEVICE_INITIALIZING; return STATUS_SUCCESS;
}
static VOID NTAPI unload(PDRIVER_OBJECT driver) { UNREFERENCED_PARAMETER(driver); }
NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT driver,PUNICODE_STRING path)
{
    ULONG i; UNREFERENCED_PARAMETER(path);
    for(i=0;i<=IRP_MJ_MAXIMUM_FUNCTION;++i) driver->MajorFunction[i]=dispatch;
    driver->MajorFunction[IRP_MJ_PNP]=pnp; driver->MajorFunction[IRP_MJ_POWER]=power;
    driver->DriverExtension->AddDevice=add; driver->DriverUnload=unload; return STATUS_SUCCESS;
}
