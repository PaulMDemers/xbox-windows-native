#include <ddk/ntddk.h>

#define XWN_IOCTL CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_WRITE_ACCESS)
static UNICODE_STRING Link;
static const ULONG Cookie[4] = {0x44554d50, 0x103, 0x10000, 1};

static NTSTATUS NTAPI Dispatch(PDEVICE_OBJECT Device, PIRP Irp)
{
    PIO_STACK_LOCATION s = IoGetCurrentIrpStackLocation(Irp);
    NTSTATUS status = STATUS_INVALID_DEVICE_REQUEST;
    (void)Device;
    if (s->MajorFunction == IRP_MJ_CREATE || s->MajorFunction == IRP_MJ_CLOSE)
        status = STATUS_SUCCESS;
    if (s->MajorFunction == IRP_MJ_DEVICE_CONTROL &&
        s->Parameters.DeviceIoControl.IoControlCode == XWN_IOCTL &&
        s->Parameters.DeviceIoControl.InputBufferLength == sizeof(Cookie) &&
        s->Parameters.DeviceIoControl.OutputBufferLength == 0 &&
        Irp->AssociatedIrp.SystemBuffer != NULL)
    {
        const ULONG *v = Irp->AssociatedIrp.SystemBuffer;
        if (v[0] == Cookie[0] && v[1] == Cookie[1] &&
            v[2] == Cookie[2] && v[3] == Cookie[3])
            KeBugCheckEx(0xe058d103, Cookie[0], Cookie[1], Cookie[2], Cookie[3]);
        status = STATUS_INVALID_PARAMETER;
    }
    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return status;
}

static VOID NTAPI Unload(PDRIVER_OBJECT Driver)
{
    IoDeleteSymbolicLink(&Link);
    if (Driver->DeviceObject) IoDeleteDevice(Driver->DeviceObject);
}

NTSTATUS NTAPI DriverEntry(PDRIVER_OBJECT Driver, PUNICODE_STRING Registry)
{
    UNICODE_STRING name;
    PDEVICE_OBJECT device;
    NTSTATUS status;
    ULONG i;
    (void)Registry;
    RtlInitUnicodeString(&name, L"\\Device\\XwnDumpTest103");
    RtlInitUnicodeString(&Link, L"\\DosDevices\\XwnDumpTest103");
    for (i = 0; i <= IRP_MJ_MAXIMUM_FUNCTION; ++i) Driver->MajorFunction[i] = Dispatch;
    Driver->DriverUnload = Unload;
    status = IoCreateDevice(Driver, 0, &name, FILE_DEVICE_UNKNOWN, 0, TRUE, &device);
    if (!NT_SUCCESS(status)) return status;
    status = IoCreateSymbolicLink(&Link, &name);
    if (!NT_SUCCESS(status)) { IoDeleteDevice(device); return status; }
    device->Flags &= ~DO_DEVICE_INITIALIZING;
    return STATUS_SUCCESS;
}
