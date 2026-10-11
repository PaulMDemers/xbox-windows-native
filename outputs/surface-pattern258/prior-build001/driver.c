/* SPDX-License-Identifier: GPL-2.0-or-later
 * Emulator-only demand diagnostic. One noncached16KiB allocation and retained
 * FileObject until reboot. No unload, release IOCTL, hardware access or GPU grant.
 */
#include <ddk/ntddk.h>
#include "arena.h"
#define X258_IOCTL CTL_CODE(FILE_DEVICE_UNKNOWN,0x858,METHOD_BUFFERED,FILE_WRITE_ACCESS)
static KMUTEX Mutex;
static X258Arena Arena;
static int passive(void *unused){(void)unused;return KeGetCurrentIrql()==PASSIVE_LEVEL;}
static int enter(void *unused)
{ LARGE_INTEGER t;(void)unused;t.QuadPart=-20000000;return KeWaitForSingleObject(&Mutex,Executive,KernelMode,FALSE,&t)==STATUS_SUCCESS; }
static void leave(void *unused){(void)unused;KeReleaseMutex(&Mutex,FALSE);}
static unsigned char *allocate(void *unused)
{ PHYSICAL_ADDRESS lo,hi,b;(void)unused;lo.QuadPart=0x100000;hi.QuadPart=0x03bfffff;b.QuadPart=0;return MmAllocateContiguousMemorySpecifyCache(X258_BYTES,lo,hi,b,MmNonCached); }
static uint64_t translate(void *unused,unsigned char *p)
{ PHYSICAL_ADDRESS a;(void)unused;a=MmGetPhysicalAddress(p);return a.QuadPart; }
static void discard(void *unused,unsigned char *p)
{ (void)unused;MmFreeContiguousMemorySpecifyCache(p,X258_BYTES,MmNonCached); }
static void retain(void *unused,void *owner){(void)unused;ObReferenceObject(owner);}
static const X258Ops Ops={0,passive,enter,leave,allocate,translate,discard,retain};
static NTSTATUS NTAPI dispatch(PDEVICE_OBJECT dev,PIRP irp)
{
    PIO_STACK_LOCATION s=IoGetCurrentIrpStackLocation(irp);
    NTSTATUS status=STATUS_INVALID_DEVICE_REQUEST;ULONG bytes=0;(void)dev;
    if(s->MajorFunction==IRP_MJ_CREATE || s->MajorFunction==IRP_MJ_CLOSE)status=STATUS_SUCCESS;
    if(s->MajorFunction==IRP_MJ_CLEANUP) {
        /* Do not access payload, free the arena or release its FileObject here.
         * A failed wait still leaves both held; a new owner cannot acquire them. */
        status=STATUS_UNSUCCESSFUL;
        if(passive(NULL) && enter(NULL)){
            if(Arena.owner==s->FileObject)Arena.closed=1;
            leave(NULL);status=STATUS_SUCCESS;
        }
    }
    if(s->MajorFunction==IRP_MJ_DEVICE_CONTROL && s->Parameters.DeviceIoControl.IoControlCode==X258_IOCTL) {
        status=STATUS_INVALID_PARAMETER;
        if(irp->AssociatedIrp.SystemBuffer && s->Parameters.DeviceIoControl.InputBufferLength==sizeof(X258Request) &&
           s->Parameters.DeviceIoControl.OutputBufferLength>=sizeof(X258Reply)) {
            X258Request q=*(X258Request *)irp->AssociatedIrp.SystemBuffer;
            x258_action(&Arena,&Ops,s->FileObject,&q,irp->AssociatedIrp.SystemBuffer);
            status=STATUS_SUCCESS;bytes=sizeof(X258Reply);
        }
    }
    irp->IoStatus.Status=status;irp->IoStatus.Information=bytes;IoCompleteRequest(irp,IO_NO_INCREMENT);return status;
}
NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT driver,PUNICODE_STRING registry)
{
    UNICODE_STRING name,link;PDEVICE_OBJECT dev;NTSTATUS s;ULONG i;(void)registry;
    KeInitializeMutex(&Mutex,0);driver->DriverUnload=NULL;
    for(i=0;i<=IRP_MJ_MAXIMUM_FUNCTION;i++)driver->MajorFunction[i]=dispatch;
    RtlInitUnicodeString(&name,L"\\Device\\XwnPattern258");RtlInitUnicodeString(&link,L"\\DosDevices\\XwnPattern258");
    s=IoCreateDevice(driver,0,&name,FILE_DEVICE_UNKNOWN,0,FALSE,&dev);if(!NT_SUCCESS(s))return s;
    s=IoCreateSymbolicLink(&link,&name);if(!NT_SUCCESS(s)){IoDeleteDevice(dev);return s;}
    dev->Flags&=~DO_DEVICE_INITIALIZING;return STATUS_SUCCESS;
}
