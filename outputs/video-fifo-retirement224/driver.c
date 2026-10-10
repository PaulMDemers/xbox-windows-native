/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only demand driver. Resident until reboot; no unload callback,
 * device-policy changes, DMA descriptors or hardware writes.224 adds bounded read-only GPU MMIO.
 */
#include <ddk/ntddk.h>
#include "context.h"
#include "retirement.h"
#ifndef X224_READS
#define X224_READS 0
#endif
#define X224_IOCTL CTL_CODE(FILE_DEVICE_UNKNOWN,0x824,METHOD_BUFFERED,FILE_WRITE_ACCESS)
#define X222_IOCTL CTL_CODE(FILE_DEVICE_UNKNOWN,0x822,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static KMUTEX Mutex;
static X222Manager Manager;
typedef struct { PIO_WORKITEM cleanup_work; } X222File;
static int passive(void *unused) { (void)unused;return KeGetCurrentIrql()==PASSIVE_LEVEL; }
static int enter(void *unused)
{
    LARGE_INTEGER timeout;(void)unused;timeout.QuadPart=-20000000;
    return KeWaitForSingleObject(&Mutex,Executive,KernelMode,FALSE,&timeout)==STATUS_SUCCESS;
}
static void leave(void *unused) { (void)unused;KeReleaseMutex(&Mutex,FALSE); }
static unsigned char *allocate(void *unused)
{
    PHYSICAL_ADDRESS low,high,boundary;(void)unused;
    low.QuadPart=0x100000;high.QuadPart=0x03bfffff;boundary.QuadPart=0;
    return MmAllocateContiguousMemorySpecifyCache(X222_BYTES,low,high,boundary,MmNonCached);
}
static uint64_t translate(void *unused,unsigned char *p)
{ PHYSICAL_ADDRESS a;(void)unused;a=MmGetPhysicalAddress(p);return a.QuadPart; }
static void release(void *unused,unsigned char *p)
{ (void)unused;MmFreeContiguousMemorySpecifyCache(p,X222_BYTES,MmNonCached); }
static void retain_owner(void *unused,void *owner)
{ (void)unused;ObReferenceObject(owner); }
static void release_owner(void *unused,void *owner)
{ (void)unused;ObDereferenceObject(owner); }
#if X224_READS
static unsigned char *FifoMap,*GraphMap;
static int gpu_read(void *unused,uint32_t index,uint32_t *value)
{
    uint32_t offset;(void)unused;
    if(index>=X224_WORDS || !FifoMap || !GraphMap)return 0;
    offset=X224Offsets[index];
    if(offset>=0x2000 && offset+4<=0x4000)
        *value=READ_REGISTER_ULONG((PULONG)(FifoMap+offset-0x2000));
    else if(offset>=0x400000 && offset+4<=0x401000)
        *value=READ_REGISTER_ULONG((PULONG)(GraphMap+offset-0x400000));
    else return 0;
    return 1;
}
static void free_maps(void)
{
    if(GraphMap){MmUnmapIoSpace(GraphMap,0x1000);GraphMap=NULL;}
    if(FifoMap){MmUnmapIoSpace(FifoMap,0x2000);FifoMap=NULL;}
}
#endif
static void retirement_query(PFILE_OBJECT owner,const X224Request *q,X224Reply *out)
{
    uint32_t i;uint32_t *p=(uint32_t *)out;
    for(i=0;i<sizeof(*out)/sizeof(*p);i++)p[i]=0;
    out->reasons=X224_NO_OWNERSHIP|X224_UNMODELED_BUSY;
    if(!passive(NULL)){out->status=X222_IRQL;return;}
    if(!enter(NULL)){out->status=X222_WAIT;return;}
    if(!Manager.memory || Manager.owner!=owner)out->status=X222_OWNER;
    else if(!q->generation || q->generation!=Manager.generation)out->status=X222_STALE;
    else {
#if X224_READS
        x224_sample(gpu_read,NULL,out);
#else
        out->status=X224_OFF;
#endif
    }
    leave(NULL);
}
static const X222Ops Ops={0,passive,enter,leave,allocate,translate,release,retain_owner,release_owner};
static NTSTATUS cleanup_status(uint32_t status)
{ return (status==X222_OK || status==X222_OWNER)?STATUS_SUCCESS:STATUS_UNSUCCESSFUL; }
static VOID NTAPI cleanup_worker(PDEVICE_OBJECT device,PVOID parameter)
{
    PIRP irp=parameter;PFILE_OBJECT file=IoGetCurrentIrpStackLocation(irp)->FileObject;
    X222Request request={X222_CLEANUP,0};X222Reply reply;ULONG attempt;(void)device;
    /* Every failed wait retains the allocation's FileObject reference. The queued
     * IRP has another reference until completion. Eight bounded two-second waits;
     * exhaustion retains the bounded CPU lease until reboot, never a GPU drain. */
    for(attempt=0;attempt<8;attempt++) {
        x222_action(&Manager,&Ops,file,&request,&reply);
        if(reply.status!=X222_WAIT)break;
    }
    irp->IoStatus.Status=cleanup_status(reply.status);irp->IoStatus.Information=0;
    IoCompleteRequest(irp,IO_NO_INCREMENT);
    ObDereferenceObject(file); /* No IRP or FsContext access after completion. */
}
static NTSTATUS NTAPI dispatch(PDEVICE_OBJECT device,PIRP irp)
{
    PIO_STACK_LOCATION s=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS status=STATUS_INVALID_DEVICE_REQUEST;ULONG bytes=0;(void)device;
    if(s->MajorFunction==IRP_MJ_CREATE) {
        X222File *file=ExAllocatePoolWithTag(NonPagedPool,sizeof(*file),0x32323258);
        status=STATUS_INSUFFICIENT_RESOURCES;
        if(file) {
            file->cleanup_work=IoAllocateWorkItem(device);
            if(file->cleanup_work){s->FileObject->FsContext=file;status=STATUS_SUCCESS;}
            else ExFreePool(file);
        }
    }
    if(s->MajorFunction==IRP_MJ_CLOSE) {
        X222File *file=s->FileObject->FsContext;
        if(file){IoFreeWorkItem(file->cleanup_work);ExFreePool(file);s->FileObject->FsContext=NULL;}
        status=STATUS_SUCCESS;
    }
    if(s->MajorFunction==IRP_MJ_CLEANUP) {
        X222Request request={X222_CLEANUP,0};X222Reply reply;
        x222_action(&Manager,&Ops,s->FileObject,&request,&reply);
        if(reply.status==X222_WAIT || reply.status==X222_IRQL) {
            X222File *file=s->FileObject->FsContext;
            if(file) {
                ObReferenceObject(s->FileObject);
                IoMarkIrpPending(irp);
                IoQueueWorkItem(file->cleanup_work,cleanup_worker,DelayedWorkQueue,irp);
                return STATUS_PENDING;
            }
        }
        status=cleanup_status(reply.status);
    }
    if(s->MajorFunction==IRP_MJ_DEVICE_CONTROL &&
       s->Parameters.DeviceIoControl.IoControlCode==X222_IOCTL) {
        status=STATUS_INVALID_PARAMETER;
        if(irp->AssociatedIrp.SystemBuffer &&
           s->Parameters.DeviceIoControl.InputBufferLength==sizeof(X222Request) &&
           s->Parameters.DeviceIoControl.OutputBufferLength>=sizeof(X222Reply)) {
            X222Request request=*(X222Request *)irp->AssociatedIrp.SystemBuffer;
            if(request.op>=X222_ALLOCATE && request.op<=X222_INFO) {
                x222_action(&Manager,&Ops,s->FileObject,&request,irp->AssociatedIrp.SystemBuffer);
                status=STATUS_SUCCESS;bytes=sizeof(X222Reply);
            }
        }
    }
    if(s->MajorFunction==IRP_MJ_DEVICE_CONTROL &&
       s->Parameters.DeviceIoControl.IoControlCode==X224_IOCTL) {
        status=STATUS_INVALID_PARAMETER;
        if(irp->AssociatedIrp.SystemBuffer &&
           s->Parameters.DeviceIoControl.InputBufferLength==sizeof(X224Request) &&
           s->Parameters.DeviceIoControl.OutputBufferLength>=sizeof(X224Reply)) {
            X224Request request=*(X224Request *)irp->AssociatedIrp.SystemBuffer;
            if(!request.reserved) {
                retirement_query(s->FileObject,&request,irp->AssociatedIrp.SystemBuffer);
                status=STATUS_SUCCESS;bytes=sizeof(X224Reply);
            }
        }
    }
    irp->IoStatus.Status=status;irp->IoStatus.Information=bytes;
    IoCompleteRequest(irp,IO_NO_INCREMENT);return status;
}
NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT driver,PUNICODE_STRING registry)
{
    UNICODE_STRING name,link;PDEVICE_OBJECT device;NTSTATUS status;ULONG i;(void)registry;
    x222_initialize(&Manager);KeInitializeMutex(&Mutex,0);
#if X224_READS
    {
        PHYSICAL_ADDRESS a;
        a.QuadPart=0xfd002000;FifoMap=MmMapIoSpace(a,0x2000,MmNonCached);
        a.QuadPart=0xfd400000;GraphMap=MmMapIoSpace(a,0x1000,MmNonCached);
        if(!FifoMap || !GraphMap){free_maps();return STATUS_INSUFFICIENT_RESOURCES;}
    }
#endif
    for(i=0;i<=IRP_MJ_MAXIMUM_FUNCTION;i++)driver->MajorFunction[i]=dispatch;
    driver->DriverUnload=NULL; /* Existing resident module is never reloaded in this trial. */
    RtlInitUnicodeString(&name,L"\\Device\\XwnResident224");
    RtlInitUnicodeString(&link,L"\\DosDevices\\XwnResident224");
    status=IoCreateDevice(driver,0,&name,FILE_DEVICE_UNKNOWN,0,FALSE,&device);
    if(!NT_SUCCESS(status)){
#if X224_READS
        free_maps();
#endif
        return status;
    }
    status=IoCreateSymbolicLink(&link,&name);
    if(!NT_SUCCESS(status)){
        IoDeleteDevice(device);
#if X224_READS
        free_maps();
#endif
        return status;
    }
    device->Flags&=~DO_DEVICE_INITIALIZING;return STATUS_SUCCESS;
}
